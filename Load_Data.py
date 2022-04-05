import random
from mylib import *

classes = pd.read_csv('DATA/ALL.csv')

db_credentials = dict(
    dbname='proj1part2',
    user='mz2715',
    password='1789',
    host='35.211.155.104'
)
schools = ['Columbia College', 'School of Engineering and Applied Science']
programs = {
    1: 'Bachelor of Science',
    2: 'Bachelor of Art',
    3: 'Master of Art',
    4: 'Master of Science',
    5: 'Non-degree Program'
}
db_connection = psycopg2.connect(**db_credentials)
cur = db_connection.cursor()

# school and programs
pid = 1
for school in schools:
    for idx in programs:
        if 'master' in programs[idx].casefold().strip():
            degree = 'Master'
        elif 'bachelor' in programs[idx].casefold().strip():
            degree = 'Bachelor'
        else:
            degree = 'Non-degree'
        add_school_program(cur, school, pid, programs[idx], degree)
        pid = pid + 1
db_connection.commit()

# classes and departments
temp_s = {
    1: schools[1],
    2: schools[1],
    3: schools[1],
    4: schools[1],
    5: schools[1],
    6: schools[0]
}
for idx, section in classes.iterrows():
    cid = section['cid']
    cname = section['cname']
    dids = get_dept(cid)
    credit = section['credit']
    for did in dids:
        add_dept_course(cur, did, department_ids[did], temp_s[did], cid, cname, credit)
db_connection.commit()

# students
Ming = dict(
    sid='mz2715',
    status='Full-time',
    studentName='Mingyuan Zhang',
    ExpectedGraduation='2022-05-22',
    AddmissionYear='2018-09-02',
    did=1,
    pid=1
)
Ziqian = dict(
    sid='zw2697',
    status='Full-time',
    studentName='Ziqian Wang',
    ExpectedGraduation='2023-05-22',
    AddmissionYear='2022-01-20',
    did=1,
    pid=4
)
Leoni = dict(
    sid='jl5592',
    status='Full-time',
    studentName='Mingyuan Zhang',
    ExpectedGraduation='2022-05-22',
    AddmissionYear='2019-09-02',
    did=1,
    pid=1
)
Tony = dict(
    sid='arp2225',
    status='Part-time',
    studentName='Antony Rafael Peters',
    ExpectedGraduation='2022-05-22',
    AddmissionYear='2020-09-02',
    did=1,
    pid=4
)
Hans = dict(
    sid='hz2576',
    status='Absent',
    studentName='Hanzhi Zhao',
    ExpectedGraduation='2023-05-22',
    AddmissionYear='2018-09-02',
    did=1,
    pid=2
)
students = [Ming, Ziqian, Leoni, Tony, Hans]
for student in students:
    student.update(cur=cur)
    add_student(**student)
db_connection.commit()
'''
# sections
locs = {'Mudd': 10.0,
        'Pupin': 5.0,
        'NWC Building': 5.0,
        'CEPSR': 1.0,
        'Chandler': 1.0,
        'Hamilton': 7.0}
for idx, section in classes.iterrows():
    cid = section['cid']
    did = get_dept(cid)[0]
    section_id = section['sid']
    instructor = section['instructor'].replace("'", "''")
    if section['location'] == section['location']:
        loc = section['location']
    else:
        temp_loc = locs.copy()
        if did == 1:
            temp_loc['Mudd'] = temp_loc['Mudd'] * 2
            temp_loc['Hamilton'] = temp_loc['Hamilton'] * 1.5
        elif did == 2:
            temp_loc['Mudd'] = temp_loc['Mudd'] * 2
            temp_loc['Chandler'] = temp_loc['Chandler'] * 3
        elif did == 3:
            temp_loc['Pupin'] = 10
        loc = random.choices(list(temp_loc.keys()), list(temp_loc.values()), k=1)[0]
    if section['Date'] == 'Spring 2022':
        current = True
    else:
        current = False
    if current:
        add_current_section(cur, section_id, cid, instructor, loc)
    else:
        add_past_section(cur, section_id, cid, instructor, '2021-09-07')
db_connection.commit()
'''
'''#prereq
for idx, section in classes.iterrows():
    cid = section['cid']
    level = [int(x) for x in cid if x.isdigit()][0]
    if level >= 4 and random.random()<0.05:
        prereq = random.choice(list(classes.cid))
        if [int(x) for x in prereq if x.isdigit()][0] <=4:
            add_prereq(cur, cid, prereq)
'''
db_connection.commit()
'''
sids = get_all_student_sid(cur)
cur.execute('SELECT psid, cid FROM past_section;')
past_secs = cur.fetchall()
for sid in list(sids.iloc[:,0]):
    num = random.randint(3, 5)
    for idx in range(0, num):
        sec = random.choice(past_secs)
        add_has_taken(cur, sec[1], sid, sec[0], 3.3+random.random())
db_connection.commit()
'''
'''
cur.execute("SELECT sid FROM student WHERE status != 'Absent';")
sids = pd.DataFrame(cur.fetchall())
cur.execute("SELECT csid, cid FROM current_section;")
curr_secs = cur.fetchall()
for sid in list(sids.iloc[:,0]):
    num = random.randint(3, 5)
    for idx in range(0, num):
        sec = random.choice(curr_secs)
        add_is_taking(cur, sec[1], sid, sec[0])
db_connection.commit()
'''

cur.close()
db_connection.close()
