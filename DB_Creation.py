from mylib import *

db_credentials = dict(
    dbname='proj1part2',
    user='mz2715',
    password='1789',
    host='35.211.155.104'
)

db_connection = psycopg2.connect(**db_credentials)
cur = db_connection.cursor()

create_cmds = dict(
    school="""CREATE TABLE school(
    sname varchar(100) PRIMARY KEY,
    pid int NOT NULL
);""",
    department="""CREATE TABLE department(
    did int PRIMARY KEY,
    dname varchar(100) NOT NULL,
    sname varchar(100) NOT NULL,
    cid varchar(12) NOT NULL
);""",
    course="""CREATE TABLE course (
    cid varchar(12) PRIMARY KEY,
    cname varchar(500) NOT NULL,
    Credit numeric(2,1) NOT NULL,
    did int NOT NULL
);""",
    offer_class="""CREATE TABLE offer_class(
    cid varchar(12) NOT NULL,
    did int NOT NULL,
    PRIMARY KEY (did, cid)
);""",
    student="""CREATE TYPE all_status AS ENUM('Full-time', 'Part-time','Absent');
CREATE TABLE student(
    sid varchar(7) PRIMARY KEY,
    Status all_status,
    StudentName varchar(50) NOT NULL,
    ExpectedGraduation date,
    AddmissionYear date NOT NULL,
    did int NOT NULL,
    pid int NOT NULL
);""",
    programs="""CREATE TABLE programs(
    pid int PRIMARY KEY,
    pname varchar(100) NOT NULL,
    Degree varchar(50),
    sname varchar(100) NOT NULL
);""",
    offer_program="""CREATE TABLE offer_program(
    sname varchar(100) NOT NULL,
    pid int NOT NULL,
    PRIMARY KEY (sname, pid)
);""",
    pursue = """CREATE TABLE pursue(
    sid varchar(7) NOT NULL,
    pid int NOT NULL,
    PRIMARY KEY (sid, pid)
);""",
    require="""CREATE TABLE require(
    cid varchar(12) NOT NULL,
    pid int NOT NULL,
    PRIMARY KEY (cid, pid)
);""",
    prerequisite="""CREATE TABLE prerequisite(
    cid varchar(12) NOT NULL,
    prereq varchar(12) NOT NULL,
    PRIMARY KEY (cid, prereq)
);""",
    current_section="""CREATE TABLE current_section(
    csid int NOT NULL,
    cid varchar(12) NOT NULL,
    instructor varchar(100), 
    loc varchar(100), 
    PRIMARY KEY (csid, cid),
    sid varchar(7) NOT NULL
);""",
    past_section="""CREATE TABLE past_section(
    psid int NOT NULL,
    cid varchar(12) NOT NULL,
    instructor varchar(100),
    offered_date date NOT NULL,
    PRIMARY KEY (psid, cid),
    sid varchar(7) NOT NULL
);""",
    has_taken="""CREATE TABLE has_taken(
    cid varchar(12) NOT NULL,
    sid varchar(7) NOT NULL,
    psid int NOT NULL,
    GPA numeric(4,3),
    CHECK (GPA >= 0 AND GPA <= 4.3),
    PRIMARY KEY (sid, psid, cid)
);""",
    is_taking="""CREATE TABLE is_taking(
    cid varchar(12) NOT NULL,
    sid varchar(7) NOT NULL,
    csid int NOT NULL,
    PRIMARY KEY (sid, psid, cid)
);""")
# Commands to add all foreign keys to avoid cyclic reference blocking
foreign_key_cmds=dict(
    school="""ALTER TABLE school 
    ADD CONSTRAINT school_offer_program_fk
        FOREIGN KEY (sname, pid) REFERENCES offer_program
            DEFERRABLE INITIALLY DEFERRED;
""",
    department="""ALTER TABLE department
    ADD CONSTRAINT department_school_fk
        FOREIGN KEY (sname) references school
            ON DELETE CASCADE,
    ADD CONSTRAINT department_offer_class_fk
        FOREIGN KEY (did, cid) references offer_class
            DEFERRABLE INITIALLY DEFERRED;
""",
    course="""ALTER TABLE course
    ADD CONSTRAINT course_offer_class_fk
        FOREIGN KEY (did, cid) references offer_class
            ON DELETE CASCADE
            DEFERRABLE INITIALLY DEFERRED;
""",
    offer_class="""ALTER TABLE offer_class
    ADD CONSTRAINT offer_class_course_fk
        FOREIGN KEY (cid) references course
            ON DELETE CASCADE,
    ADD CONSTRAINT offer_class_department_fk
        FOREIGN KEY (did) references department
            ON DELETE CASCADE;
""",
    student="""ALTER TABLE student
    ADD CONSTRAINT student_department_fk
        FOREIGN KEY (did) references department
            ON DELETE CASCADE,
    ADD CONSTRAINT student_pursue_fk
        FOREIGN KEY (sid, pid) references pursue
            DEFERRABLE INITIALLY DEFERRED;
""",
    programs="""ALTER TABLE programs
    ADD CONSTRAINT programs_offer_program_fk
        FOREIGN KEY (sname, pid) references offer_program
            ON DELETE CASCADE
            DEFERRABLE INITIALLY DEFERRED;
""",
    offer_program="""ALTER TABLE offer_program
    ADD CONSTRAINT offer_program_school_fk
        FOREIGN KEY (pid) references programs,
    ADD CONSTRAINT offer_program_program_fk
        FOREIGN KEY (sname) references school
            ON DELETE CASCADE;
""",
    purse="""ALTER TABLE pursue
    ADD CONSTRAINT pursue_student_fk
        FOREIGN KEY (sid) references student
            ON DELETE CASCADE,
    ADD CONSTRAINT pursue_programs_fk
        FOREIGN KEY (pid) references programs
            ON DELETE CASCADE;
""",
    require="""ALTER TABLE require
    ADD CONSTRAINT require_programs_fk
        FOREIGN KEY (pid) references programs
            ON DELETE CASCADE,
    ADD CONSTRAINT require_course_fk
        FOREIGN KEY (cid) references course;
""",
    prerequisite="""ALTER TABLE prerequisite
    ADD CONSTRAINT prerequisite_course_cid_fk
        FOREIGN KEY (cid) references course
            ON DELETE CASCADE,
    ADD CONSTRAINT prerequisite_course_prereq_fk
        FOREIGN KEY (prereq) references course (cid);
""",
    current_section="""ALTER TABLE current_section
    ADD CONSTRAINT current_section_course_fk
        FOREIGN KEY (cid) references course
            ON DELETE CASCADE,
    ADD CONSTRAINT current_section_is_taking_fk
        FOREIGN KEY (sid, csid, cid) references is_taking (sid, csid, cid)
            ON DELETE CASCADE
            DEFERRABLE INITIALLY DEFERRED;
""",
    past_section="""ALTER TABLE past_section
    ADD CONSTRAINT past_section_course_fk
        FOREIGN KEY (cid) references course
            ON DELETE CASCADE,
    ADD CONSTRAINT past_section_has_taken_fk
        FOREIGN KEY (sid, psid, cid) references has_taken (sid, psid, cid)
            DEFERRABLE INITIALLY DEFERRED;
""",
    has_taken="""ALTER TABLE has_taken
    ADD CONSTRAINT has_taken_past_section_fk
        FOREIGN KEY (psid, cid) references past_section(psid, cid)
            ON DELETE CASCADE,
    ADD CONSTRAINT has_taken_student_fk
        FOREIGN KEY (sid) references student
            ON DELETE CASCADE;
""",
    is_taking="""ALTER TABLE is_taking
    ADD CONSTRAINT is_taking_current_section_fk
        FOREIGN KEY (csid, cid) references current_section
            ON DELETE CASCADE,
    ADD CONSTRAINT is_taking_student_fk
        FOREIGN KEY (sid) references student
            ON DELETE CASCADE;
""")

for table in create_cmds:
    cur.execute(create_cmds[table])
db_connection.commit()
for table in foreign_key_cmds:
    cur.execute(foreign_key_cmds[table])
db_connection.commit()
cur.close()
db_connection.close()
