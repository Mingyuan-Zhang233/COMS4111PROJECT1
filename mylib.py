"""This contains some useful methods I wrote for COMS4111 Project 1
Auth: Mingyuan Zhang
"""

import pandas as pd
import os
import datetime
import sqlalchemy
import psycopg2
import click
from flask import Flask, request
import flask
from IPython.display import display

department_ids = {
    1: 'Electrical Engineering',
    2: 'Computer Science',
    3: 'Biomedical Engineering',
    4: 'Industrial Engineering',
    5: 'Mechanical Engineering',
    6: 'Biology'
}
schools = ['Columbia College', 'School of Engineering and Applied Science']
programs = {
    1: 'Bachelor of Science',
    2: 'Bachelor of Art',
    3: 'Master of Art',
    4: 'Master of Science',
    5: 'Non-degree Program'
}
table_names = (
    'school', 'department', 'course', 'offer_class', 'student', 'programs', 'offer_program', 'purse', 'require',
    'prerequisite', 'current_section', 'past_section', 'has_taken', 'is_taking')


def fetch_all(cur, disp=False):
    """Fetch all results and return as a dataframe

    :param cur: the current cursor
    :param disp: if true, display the result
    :return: the result as a pandas dataframe
    """
    result = pd.DataFrame(cur.fetchall())
    if disp:
        print('\n'.join(result.to_string(index=False).split('\n')[1:]))
    return result


def get_dept(cid):
    """Get deppartment from course ID

    :param cid: str: course id
    :return: list of dept ids that it
    """
    tag = cid[0:4]
    code_names = {
        'ELEN': [1],
        'CSEE': [1, 2],
        'ECBM': [1, 2, 3],
        'EEME': [1, 5],
        'EECS': [1, 2],
        'EEOR': [1, 4],
        'BMEB': [1, 3, 6],
        'BMEE': [1, 3],
        'EEBM': [1, 3],
        'COMS': [2],
        'CSOR': [2, 4],
        'CBMF': [2, 3],
        'ENGI': [2],
        'BMEN': [3]
    }
    return code_names[tag]


def add_school_program(cur, sname, pid, pname, degree):
    cmd = f'''BEGIN;
    INSERT INTO school VALUES
        ('{sname}', {pid})
        ON CONFLICT DO NOTHING;
    INSERT INTO programs VALUES
        ({pid}, '{pname}', '{degree}', '{sname}')
        ON CONFLICT DO NOTHING;
    INSERT INTO offer_program VALUES
        ('{sname}', {pid})
        ON CONFLICT DO NOTHING;
COMMIT;'''.format(sname=sname, pid=pid, pname=pname, degree=degree)
    cur.execute(cmd)


def add_dept_course(cur, did, dname, sname, cid, cname, credit):
    cmd = f'''BEGIN;
        INSERT INTO department VALUES
            ({did}, '{dname}', '{sname}', '{cid}')
            ON CONFLICT DO NOTHING;
        INSERT INTO course VALUES
            ('{cid}', '{cname}', {credit}, {did})
            ON CONFLICT DO NOTHING;
        INSERT INTO offer_class VALUES
            ('{cid}', {did})
            ON CONFLICT DO NOTHING;
COMMIT;'''.format(sname=sname, did=did, cname=cname, dname=dname, cid=cid, credit=credit)
    cur.execute(cmd)


def add_student(cur, sid, status, studentName, ExpectedGraduation, AddmissionYear, did, pid):
    """Add student to table

    :param did:
    :param pid:
    :param cur: cursor
    :param sid:
    :param status: either one of 'Full-time', 'Part-time','Absent'
    :param studentName:
    :param ExpectedGraduation: Date in format "YYYY-MM-DD"
    :param AddmissionYear:
    :return: None
    """
    cmd = f'''BEGIN;
        INSERT INTO student VALUES
            ('{sid}', '{status}', '{studentName}', '{ExpectedGraduation}', '{AddmissionYear}', {did}, {pid})
            ON CONFLICT DO NOTHING;
        INSERT INTO pursue VALUES
            ('{sid}', {pid})
            ON CONFLICT DO NOTHING;
COMMIT;'''.format(sid=sid, status=status, studentName=studentName, ExpectedGraduation=ExpectedGraduation,
                  AddmissionYear=AddmissionYear, did=did, pid=pid)
    cur.execute(cmd)


def add_pursue(cur, sid, pid):
    cmd = f'''INSERT INTO pursue VALUES
            ('{sid}', {pid})
            ON CONFLICT DO NOTHING;
'''.format(pid=pid, sid=sid)
    cur.execute(cmd)


def add_past_section(cur, psid, cid, instructor, offered_date):
    cmd = f'''INSERT INTO past_section VALUES
        ({psid}, '{cid}', '{instructor}', '{offered_date}')
        ON CONFLICT DO NOTHING;
'''.format(psid=psid, cid=cid, instructor=instructor, offered_date=offered_date)
    cur.execute(cmd)


def add_current_section(cur, csid, cid, instructor, loc):
    cmd = f'''INSERT INTO current_section VALUES
        ({csid}, '{cid}', '{instructor}', '{loc}')
        ON CONFLICT DO NOTHING;
'''.format(csid=csid, cid=cid, instructor=instructor, loc=loc)
    cur.execute(cmd)


def add_require(cur, cid, pid):
    cmd = f'''INSERT INTO require VALUES
        ('{cid}', {pid})
        ON CONFLICT DO NOTHING;
'''.format(cid=cid, pid=pid)
    cur.execute(cmd)


def add_prereq(cur, cid, prereq):
    cmd = f'''INSERT INTO prerequisite VALUES
        ('{cid}', '{prereq}')
        ON CONFLICT DO NOTHING;
'''.format(cid=cid, prereq=prereq)
    cur.execute(cmd)


def get_all_student_sid(cur):
    cur.execute("SELECT student.sid FROM student;")
    return fetch_all(cur)


def add_has_taken(cur, cid, sid, psid, GPA):
    cmd = f'''INSERT INTO has_taken VALUES
        ('{cid}', '{sid}', {psid}, {GPA})
        ON CONFLICT DO NOTHING;
'''.format(cid=cid, sid=sid, psid=psid, GPA=GPA)
    cur.execute(cmd)


def add_is_taking(cur, cid, sid, csid):
    cmd = f'''INSERT INTO is_taking VALUES
            ('{cid}', '{sid}', {csid})
            ON CONFLICT DO NOTHING;
    '''.format(cid=cid, sid=sid, csid=csid)
    cur.execute(cmd)


def show_classes_by_student_name(cur, sname: str):
    cmd = f'''SELECT course.cname
                FROM course, has_taken, student
                WHERE course.cid=has_taken.cid AND student.sid=has_taken.sid AND student.studentname='{sname}';
    '''.format(sname=sname)
    cur.execute(cmd)
    clases_taken = cur.fetchall()
    cmd = f'''SELECT course.cname
                    FROM course, is_taking, student
                    WHERE course.cid=is_taking.cid AND student.sid=is_taking.sid AND student.studentname='{sname}';
    '''.format(sname=sname)
    cur.execute(cmd)
    clases_taking = cur.fetchall()
    return clases_taken, clases_taking

def is_valid_date(lst_date):
    result = True
    for date in lst_date:
       try:
           datetime.date.fromisoformat(date)
       except ValueError:
           result = False
    return result


def get_all_sections(cur, tag):
    if tag == 'past':
        cmd = '''SELECT *
                FROM past_section;'''
    else:
        cmd = '''SELECT *
                FROM current_section;'''
    cur.execute(cmd)
    return cur.fetchall()


def get_section_by_cid(cur, tag, cid):
    if tag == 'past':
        cmd = f'''SELECT *
                FROM past_section
                where past_section.cid = '{cid}';
        '''.format(cid=cid)
    else:
        cmd = f'''SELECT *
                FROM current_section
                where current_section.cid = '{cid}';
        '''.format(cid=cid)
    cur.execute(cmd)
    return cur.fetchall()


def get_section_by_instructor(cur, tag, ins):
    if tag == 'past':
        cmd = f'''SELECT *
                FROM past_section
                where past_section.instructor = '{ins}';
        '''.format(ins=ins)
    else:
        cmd = f'''SELECT *
                FROM current_section
                where current_section.instructor = '{ins}';
        '''.format(ins=ins)
    cur.execute(cmd)
    return cur.fetchall()


def get_section_by_location(cur, loc):
    cmd = f'''SELECT *
            FROM current_section
            where current_section.loc = '{loc}';
    '''.format(loc=loc)
    cur.execute(cmd)
    return cur.fetchall()

def get_student_by_id(cur, sid):
    cmd = f'''SELECT student.sid, student.studentname, department.dname, student.status, programs.pname, student.expectedgraduation, student.addmissionyear 
            FROM student, department, programs, pursue
            WHERE student.sid = '{sid}' AND pursue.pid=programs.pid AND student.did = department.did AND student.sid=pursue.sid;
    '''.format(sid=sid)
    cur.execute(cmd)
    return cur.fetchall()


def run_statment(cur, st):
    cur.execute(st)
    return cur.fetchall()