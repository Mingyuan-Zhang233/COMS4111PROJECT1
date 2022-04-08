from mylib import *

db_credentials = dict(
    dbname='proj1part2',
    user='mz2715',
    password='1789',
    host='35.211.155.104'
)

db_connection = psycopg2.connect(**db_credentials)
cur = db_connection.cursor()

app = Flask(__name__)
SESSION_TYPE = "redis"
app.config.update(SECRET_KEY=os.urandom(24))
messages = [{'title': 'Add Records',
             'option': [{'content': 'Adding Students',
                         'link': '/add_a_student/'},
                        {'content': 'Adding Courses',
                         'link': '/add_course/'},
                        {'content': 'Adding Sections',
                         'link': '/add_section/'},
                        {'content': 'Record Course Taken',
                         'link': '/record_course/'}]
             },
            {'title': 'View Records',
             'option': [{'content': 'View student current/past courses',
                         'link': '/student/'},
                        {'content': 'View student info',
                         'link': '/sinfo/'},
                        {'content': 'Find Sections',
                         'link': '/section/'}]
             },
            {'title': 'Administrator',
             'option': [{'content': 'Manage Database by SQL Statments',
                         'link': '/admin/'}]
             }
            ]


@app.route('/admin/', methods=['GET', 'POST'])
def run_SQL():
    if request.method == 'POST':
        statement = request.form['content']
        result = run_statment(cur, statement)
        db_connection.commit()
        return flask.render_template('run_SQL.html', data=result)
    return flask.render_template('run_SQL.html', data=[[]])


@app.route('/')
def index():
    return flask.render_template('index.html', messages=messages)


@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flask.flash('Title is required!')
        elif not content:
            flask.flash('Content is required!')
        else:
            messages.append({'title': title, 'content': content})
            return flask.redirect(flask.url_for('index'))
    return flask.render_template('create.html')


@app.route('/add_section/', methods=['GET', 'POST'])
def add_section():
    if request.method == 'POST':
        cid = request.form['cid']
        csid = request.form['csid']
        ins = request.form['ins']
        loc = request.form['loc']
        try:
            csid = int(csid)
        except ValueError:
            pass
        if not isinstance(csid, int):
            flask.flash('Section number must be integer')
        else:
            add_current_section(cur, csid, cid, ins, loc)
            db_connection.commit()
    return flask.render_template('add_section.html')


@app.route('/add_course/', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        cid = request.form['cid']
        cname = request.form['cname']
        credit = request.form['credit']
        credit = round(float(credit), 2)
        sname = request.form['sch']
        try:
            deps = get_dept(cid)
            for did in deps:
                add_dept_course(cur, did, department_ids[did], sname, cid, cname, credit)
            db_connection.commit()
        except KeyError:
            flask.flash('Unknow Department Code in CID!')
    return flask.render_template('add_course.html')


@app.route('/add_a_student/', methods=('GET', 'POST'))
def add_a_student():
    if request.method == 'POST':
        sname = request.form['sname']
        uni = request.form['uni']
        did = int(request.form['did'])
        status = request.form['status']
        exp = request.form['exp']
        addm = request.form['addm']
        pid = int(request.form['pid'])
        print(list(request.form.values()))
        if '' in list(request.form.values()):
            flask.flash('All fields must be filled!')
        elif is_valid_date([exp, addm]):
            flask.flash('Date incorrect, check format!')
        else:
            add_student(cur, uni, status, sname, exp, addm, did, pid)
            db_connection.commit()
            return flask.render_template('success.html')
    return flask.render_template('add_student.html')


@app.route('/record_course/', methods=['GET', 'POST'])
def record_course():
    if request.method == 'POST':
        cid = request.form['cid']
        csid = request.form['csid']
        sid = request.form['sid']
        try:
            csid = int(csid)
        except ValueError:
            pass
        if not isinstance(csid, int):
            flask.flash('Section number must be integer')
        elif csid <= 0:
            flask.flash('Section number invalid.')
        else:
            add_is_taking(cur, cid, sid, csid)
            db_connection.commit()
    return flask.render_template('record_course.html')


@app.route('/student/', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        sname = request.form['sname']
        tag = request.form['tag'] == 'curr'
        if tag:
            result = show_classes_by_student_name(cur, sname)[1]
            title = 'Current Courses of ' + sname
        else:
            result = show_classes_by_student_name(cur, sname)[0]
            title = 'Past Courses of ' + sname
        if len(result) == 0:
            flask.flash('There is not section of class associated with this student!')
        else:
            return flask.render_template('display.html', data=result, title=title)
    return flask.render_template('student.html')


@app.route('/section/', methods=['GET', 'POST'])
def section():
    if request.method == 'POST':
        choice = request.form['choice']
        value = request.form['inp']
        tag = request.form['tag']
        if value == '':
            data = get_all_sections(cur, tag)
        elif choice == 'cid':
            data = get_section_by_cid(cur, tag, value)
        elif choice == 'ins':
            data = get_section_by_instructor(cur, tag, value)
        elif choice == 'loc':
            data = get_section_by_location(cur, value)
        return flask.render_template('display.html', data=data, title='Filtered Sections')
    return flask.render_template('section.html')


@app.route('/display/')
def display(res):
    table = res[0]
    title = res[1]
    return flask.render_template('display.html', data=table, title=title)


@app.route('/sinfo/', methods=['GET', 'POST'])
def sinfo():
    if request.method == 'POST':
        uni = request.form['sid']
        info = get_student_by_id(cur, uni)
        head = ['UNI: ', 'Name: ', 'Department: ', 'Status: ', 'Programs: ', 'Expected Graduation: ', 'Admitted Year: ']
        data = [[], [], [], [], [], [], []]
        if len(info) == 0:
            flask.flash('Unknown UNI. Student DNE.')
        else:
            for row in info:
                for idx, lst in enumerate(data):
                    data[idx].append(row[idx])
            for idx, lst in enumerate(data):
                data[idx] = list(set(lst))
                data[idx].insert(0, head[idx])
        return flask.render_template('display.html', data=data, title='Student Info')
    return flask.render_template('student_info.html')


app.run(host='0.0.0.0', port=80)
