from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)
app.config['DEBUG'] = True

dbconn = None
connection = None

#define database connection
def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

#define homebase_page
@app.route("/")
def home():
    return render_template("home.html")

#define method for passing data for List of drivers page
@app.route("/listdrivers")
def listdrivers():
    connection = getCursor()
    # Modify the SQL query to join driver and car tables and order by surname and first name
    connection.execute("SELECT driver.driver_id, driver.first_name, driver.surname, car.model, car.drive_class, driver.age,driver.date_of_birth FROM driver JOIN car ON driver.car = car.car_num ORDER BY driver.surname, driver.first_name;")
    driverList = connection.fetchall()
    return render_template("driverlist.html", driver_list = driverList)    

#define method for passing data for List of courses
@app.route("/listcourses")
def listcourses():
    connection = getCursor()
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list = courseList)

#define method for passing data for Bar graph
@app.route("/graph")
def showgraph():
    connection = getCursor()

# Create a Common Table Expression (CTE) named CourseTimes
# This CTE calculates the best times for each driver on each course
# For each course (A to F), find the minimum time (best run) for the driver
# If no time is found, label it as 'dnf' (did not finish)

# Create another CTE named OverallResults
# This CTE calculates the overall result for each driver across all courses
# If the driver's age is less than or equal to 18, append '(J)' to their first name
# Calculate the overall result by summing up all course times
# If any course time is 'dnf', label the overall result as 'NQ' (not qualified)

# Create another CTE named RankedResults
# This CTE assigns a ranking to each driver based on their overall result
# If the overall result is 'NQ', don't assign a ranking
# Otherwise, assign a ranking based on the overall result (ascending order)

# Finally, select the top 5 drivers based on their overall results
# Drivers with 'NQ' are placed at the end

    query = """
        WITH CourseTimes AS (
    SELECT driver.driver_id,
           driver.first_name,
           driver.surname,
           driver.age,
           car.model,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'A' THEN run.seconds END), 2), 'dnf') as course_A_time,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'B' THEN run.seconds END), 2), 'dnf') as course_B_time,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'C' THEN run.seconds END), 2), 'dnf') as course_C_time,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'D' THEN run.seconds END), 2), 'dnf') as course_D_time,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'E' THEN run.seconds END), 2), 'dnf') as course_E_time,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'F' THEN run.seconds END), 2), 'dnf') as course_F_time
    FROM driver
    JOIN car ON driver.car = car.car_num
    LEFT JOIN run ON driver.driver_id = run.dr_id
    GROUP BY driver.driver_id
),
OverallResults AS (
    SELECT driver_id,
           CASE WHEN age <= 18 THEN CONCAT(first_name, ' (J)') ELSE first_name END AS first_name,
           surname,
           model,
           course_A_time,
           course_B_time,
           course_C_time,
           course_D_time,
           course_E_time,
           course_F_time,
           CASE WHEN course_A_time = 'dnf' OR course_B_time = 'dnf' OR course_C_time = 'dnf' OR course_D_time = 'dnf' OR course_E_time = 'dnf' OR course_F_time = 'dnf'
                THEN 'NQ'
                ELSE FORMAT(course_A_time + course_B_time + course_C_time + course_D_time + course_E_time + course_F_time, 2)
           END AS overall_result
    FROM CourseTimes
)
, RankedResults AS (
    SELECT *, 
           CASE 
               WHEN overall_result = 'NQ' THEN NULL
               ELSE ROW_NUMBER() OVER (ORDER BY overall_result)
           END AS ranking
    FROM OverallResults
)
SELECT CONCAT(driver_id,' ',first_name,surname) as playeridandname,overall_result
FROM RankedResults
ORDER BY CASE WHEN overall_result = 'NQ' THEN 1 ELSE 0 END, overall_result LIMIT 5;
    """
    
    connection.execute(query)
    results = connection.fetchall()
    
    # Extracting names and overall results from the fetched data
    bestDriverList = [row[0] for row in results]  # Assuming driver ID is in the first column and name in the second
    resultsList = [row[1] for row in results]  # Assuming overall result is in the third column
    
    return render_template("top5graph.html", name_list = bestDriverList, value_list = resultsList)

# old version
# #define method for passing data for Driver's run details
# @app.route("/driverrundetail",methods=['GET', 'POST'])
# def showdriverrundetail():
#         connection = getCursor()
#         # retrieve data from table driver for show in driverrundetail.html drop down widget
#         connection.execute("SELECT * FROM driver;")
#         driverlist = connection.fetchall()

#         if request.method == 'GET':
#             driverid = request.args.get('driverid')
#             sql="""SELECT 
#     d.driver_id AS "Driver ID",
#     CONCAT(d.first_name, ' ', d.surname) AS "Driver Name",
#     c.name AS "Course Name",
#     r.run_num AS "Run Num",
#     r.seconds AS "Time",
#     COALESCE(r.cones, 0) AS "Cones",
#     COALESCE(r.wd, 0) AS "WD",
#     ROUND(r.seconds + COALESCE(r.cones, 0) * 2 + COALESCE(r.wd, 0) * 10,2) AS "Run Total"  -- Assuming each cone adds 2 seconds and WD adds 10 seconds
# FROM 
#     run r
# JOIN driver d ON r.dr_id = d.driver_id
# JOIN course c ON r.crs_id = c.course_id where d.driver_id = %s
# ORDER BY d.driver_id, c.name, r.run_num;"""
#              # retrieve data from table run,driver,course for show   driverdetail  in driverrundetail.html
#             connection.execute(sql, (driverid,))
#             driverdetail =  connection.fetchall()
#             return render_template('driverrundetail.html', driverdetail=driverdetail,drivers_list=driverlist)

    
#         if request.method == 'POST':
#             if 'Resets' in request.form:
#                  sql = """SELECT 
#     d.driver_id AS "Driver ID",
#     CONCAT(d.first_name, ' ', d.surname) AS "Driver Name",
#     c.name AS "Course Name",
#     r.run_num AS "Run Num",
#     r.seconds AS "Time",
#     COALESCE(r.cones, 0) AS "Cones",
#     COALESCE(r.wd, 0) AS "WD",
#     ROUND(r.seconds + COALESCE(r.cones, 0) * 2 + COALESCE(r.wd, 0) * 10,2) AS "Run Total"  -- Assuming each cone adds 2 seconds and WD adds 10 seconds
# FROM 
#     run r
# JOIN driver d ON r.dr_id = d.driver_id
# JOIN course c ON r.crs_id = c.course_id where d.driver_id = %s
# ORDER BY d.driver_id, c.name, r.run_num;"""
#                  connection.execute(sql)
#                  driverdetail = connection.fetchall()
#                  return render_template('driverrundetail.html', drivers_list=driverlist,driverdetail=driverdetail) 
#             else:           
#                  driverid = request.form.get('driver')
#                  sql="""SELECT 
#     d.driver_id AS "Driver ID",
#     CONCAT(d.first_name, ' ', d.surname) AS "Driver Name",
#     c.name AS "Course Name",
#     r.run_num AS "Run Num",
#     r.seconds AS "Time",
#     COALESCE(r.cones, 0) AS "Cones",
#     COALESCE(r.wd, 0) AS "WD",
#     ROUND(r.seconds + COALESCE(r.cones, 0) * 2 + COALESCE(r.wd, 0) * 10,2) AS "Run Total"  -- Assuming each cone adds 2 seconds and WD adds 10 seconds
# FROM 
#     run r
# JOIN driver d ON r.dr_id = d.driver_id
# JOIN course c ON r.crs_id = c.course_id where d.driver_id = %s
# ORDER BY d.driver_id, c.name, r.run_num;"""
#              # retrieve data from table run,driver,course for show   driverdetail  in driverrundetail.html
#                  connection.execute(sql, (driverid,))
#                  driverdetail =  connection.fetchall()
#                  return render_template('driverrundetail.html', driverdetail=driverdetail,drivers_list=driverlist)

#         return render_template('driverrundetail.html', drivers_list=driverlist)


@app.route("/driverrundetail",methods=['GET', 'POST'])
def showdriverrundetail():
    connection = getCursor()
    connection.execute("SELECT * FROM driver;")
    driverlist = connection.fetchall()

    catchallsql = """SELECT 
    d.driver_id AS "Driver ID",
    CONCAT(d.first_name, ' ', d.surname) AS "Driver Name",
    c.name AS "Course Name",
    r.run_num AS "Run Num",
    r.seconds AS "Time",
    COALESCE(r.cones, 0) AS "Cones",
    COALESCE(r.wd, 0) AS "WD",
    ROUND(r.seconds + COALESCE(r.cones, 0) * 2 + COALESCE(r.wd, 0) * 10,2) AS "Run Total"  
FROM 
    run r
JOIN driver d ON r.dr_id = d.driver_id
JOIN course c ON r.crs_id = c.course_id 
ORDER BY d.driver_id, c.name, r.run_num;"""
    connection.execute(catchallsql)
    driverdetail = connection.fetchall()


    if request.method == 'GET':
        driverid = request.args.get('driverid')
        if driverid:
            sql = """SELECT 
    d.driver_id AS "Driver ID",
    CONCAT(d.first_name, ' ', d.surname) AS "Driver Name",
    c.name AS "Course Name",
    r.run_num AS "Run Num",
    r.seconds AS "Time",
    COALESCE(r.cones, 0) AS "Cones",
    COALESCE(r.wd, 0) AS "WD",
    ROUND(r.seconds + COALESCE(r.cones, 0) * 2 + COALESCE(r.wd, 0) * 10,2) AS "Run Total"  -- Assuming each cone adds 2 seconds and WD adds 10 seconds
FROM 
    run r
JOIN driver d ON r.dr_id = d.driver_id
JOIN course c ON r.crs_id = c.course_id where d.driver_id = %s
ORDER BY d.driver_id, c.name, r.run_num;""" 
            connection.execute(sql, (driverid,))
            driverdetail = connection.fetchall()
            return render_template('driverrundetail.html', driverdetail=driverdetail, drivers_list=driverlist)

    if request.method == 'POST':
        if 'reset' in request.form:
            sql = """SELECT 
    d.driver_id AS "Driver ID",
    CONCAT(d.first_name, ' ', d.surname) AS "Driver Name",
    c.name AS "Course Name",
    r.run_num AS "Run Num",
    r.seconds AS "Time",
    COALESCE(r.cones, 0) AS "Cones",
    COALESCE(r.wd, 0) AS "WD",
    ROUND(r.seconds + COALESCE(r.cones, 0) * 2 + COALESCE(r.wd, 0) * 10,2) AS "Run Total"  -- Assuming each cone adds 2 seconds and WD adds 10 seconds
FROM 
    run r
JOIN driver d ON r.dr_id = d.driver_id
JOIN course c ON r.crs_id = c.course_id 
ORDER BY d.driver_id, c.name, r.run_num;""" # This should be an SQL query that gets the details of all drivers
            connection.execute(sql)
            driverdetail = connection.fetchall()
            return render_template('driverrundetail.html', driverdetail=driverdetail, drivers_list=driverlist)
        else:
            driverid = request.form.get('driver')
            sql = """SELECT 
    d.driver_id AS "Driver ID",
    CONCAT(d.first_name, ' ', d.surname) AS "Driver Name",
    c.name AS "Course Name",
    r.run_num AS "Run Num",
    r.seconds AS "Time",
    COALESCE(r.cones, 0) AS "Cones",
    COALESCE(r.wd, 0) AS "WD",
    ROUND(r.seconds + COALESCE(r.cones, 0) * 2 + COALESCE(r.wd, 0) * 10,2) AS "Run Total"  -- Assuming each cone adds 2 seconds and WD adds 10 seconds
FROM 
    run r
JOIN driver d ON r.dr_id = d.driver_id
JOIN course c ON r.crs_id = c.course_id where d.driver_id = %s
ORDER BY d.driver_id, c.name, r.run_num;"""
            connection.execute(sql, (driverid,))
            driverdetail = connection.fetchall()
            return render_template('driverrundetail.html', driverdetail=driverdetail, drivers_list=driverlist)

    return render_template('driverrundetail.html',driverdetail=driverdetail, drivers_list=driverlist)





#define method for passing data for Overall results
@app.route("/listoverallresult")
def showoverallresult():
    connection = getCursor()

# Define a Common Table Expression (CTE) named CourseTimes
# This CTE calculates the best times for each driver on each course (A to F)
# For each course, find the minimum time (best run) for the driver
# If no time is found, label it as 'dnf' (did not finish)

# Define another CTE named OverallResults
# This CTE calculates the overall result for each driver across all courses
# If the driver's age is less than or equal to 18, append '(J)' to their first name
# Calculate the overall result by summing up all course times
# If any course time is 'dnf', label the overall result as 'NQ' (not qualified)

# Define another CTE named RankedResults
# This CTE assigns a ranking to each driver based on their overall result
# If the overall result is 'NQ', don't assign a ranking
# Otherwise, assign a ranking based on the overall result (ascending order)

# Finally, select the drivers and their details
# Assign a 'cup' to the top-ranked driver and 'prize' to the next four
# Drivers with 'NQ' are placed at the end of the list

    connection.execute("""
        WITH CourseTimes AS (
    SELECT driver.driver_id,
           driver.first_name,
           driver.surname,
           driver.age,
           car.model,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'A' THEN run.seconds END), 2), 'dnf') as course_A_time,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'B' THEN run.seconds END), 2), 'dnf') as course_B_time,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'C' THEN run.seconds END), 2), 'dnf') as course_C_time,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'D' THEN run.seconds END), 2), 'dnf') as course_D_time,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'E' THEN run.seconds END), 2), 'dnf') as course_E_time,
           COALESCE(ROUND(MIN(CASE WHEN run.crs_id = 'F' THEN run.seconds END), 2), 'dnf') as course_F_time
    FROM driver
    JOIN car ON driver.car = car.car_num
    LEFT JOIN run ON driver.driver_id = run.dr_id
    GROUP BY driver.driver_id
),
OverallResults AS (
    SELECT driver_id,
           CASE WHEN age <= 18 THEN CONCAT(first_name, ' (J)') ELSE first_name END AS first_name,
           surname,
           model,
           course_A_time,
           course_B_time,
           course_C_time,
           course_D_time,
           course_E_time,
           course_F_time,
           CASE WHEN course_A_time = 'dnf' OR course_B_time = 'dnf' OR course_C_time = 'dnf' OR course_D_time = 'dnf' OR course_E_time = 'dnf' OR course_F_time = 'dnf'
                THEN 'NQ'
                ELSE FORMAT(course_A_time + course_B_time + course_C_time + course_D_time + course_E_time + course_F_time, 2)
           END AS overall_result
    FROM CourseTimes
)
, RankedResults AS (
    SELECT *, 
           CASE 
               WHEN overall_result = 'NQ' THEN NULL
               ELSE ROW_NUMBER() OVER (ORDER BY overall_result)
           END AS ranking
    FROM OverallResults
)
SELECT driver_id, first_name, surname, model, course_A_time, course_B_time, course_C_time, course_D_time, course_E_time, course_F_time,
       CASE 
           WHEN ranking = 1 THEN CONCAT(overall_result, ' cup')
           WHEN ranking BETWEEN 2 AND 5 THEN CONCAT(overall_result, ' prize')
           ELSE overall_result
       END AS overall_result
FROM RankedResults
ORDER BY CASE WHEN overall_result = 'NQ' THEN 1 ELSE 0 END, overall_result;

    """)
    overallResults = connection.fetchall()
    return render_template('overallresults.html', results=overallResults)




############################################# Admin Functions Begins Here#############################################


#define method for Admin Page
@app.route("/admin")
def showadminmain():
        return render_template('adminmain.html')


#define method for Admin Page-----Junior driver list,passing data from database to junior_drivers.html
@app.route('/admin/junior_drivers')
def juniordrivers():
    connection = getCursor()
# Select the first name, surname, and age of the driver.
# Also, select the first name of the caregiver associated with the driver.
# Left join the driver table on itself to get the caregiver's details.
# The alias 'caregiver' is used to differentiate between the driver and their caregiver.
# Filter the results to only include drivers who are 18 years old or younger.
# Order the results first by age in descending order, then by the driver's surname.
    query = """
    SELECT driver.first_name, driver.surname, driver.age, caregiver.first_name AS caregiver_name
    FROM driver
    LEFT JOIN driver AS caregiver ON driver.caregiver = caregiver.driver_id
    WHERE driver.age <= 25 and driver.age >=12
    ORDER BY driver.age DESC, driver.surname;
    """
    connection.execute(query)
    results = connection.fetchall()
    print(results)
    return render_template('junior_drivers.html', drivers=results)


#define method for Admin Page-----Driver search,passing data from database to junior_drivers.html
@app.route('/admin/search_drivers', methods=['GET', 'POST'])
def searchdrivers():
    connection = getCursor()
    query = """
    SELECT driver.first_name, driver.surname, driver.age, car.model
    FROM driver
    JOIN car ON driver.car = car.car_num
    """
    
    if request.method == 'POST':
        if 'reset' in request.form:
            # If the reset button was clicked, fetch all drivers
            connection.execute(query)
        else:
            # use driver_name to query 
            driver_name = request.form.get('search_query')
            if driver_name:
                connection.execute("""SELECT driver.first_name, driver.surname, driver.age, car.model
    FROM driver
    JOIN car ON driver.car = car.car_num where driver.first_name LIKE %s OR driver.surname LIKE %s""", ('%' + driver_name + '%', '%' + driver_name + '%'))
    else:
        connection.execute(query)
        
    drivers = connection.fetchall()
    return render_template('driver_search.html', drivers=drivers)


#define method for Admin Page-----Edit runs
@app.route('/admin/edit_runs', methods=['GET', 'POST'])
def edit_runs():
    connection = getCursor()

    # Load all drivers and courses for the dropdowns
    connection.execute("SELECT driver_id, first_name, surname FROM driver")
    drivers = connection.fetchall()

    connection.execute("SELECT course_id, name FROM course")
    courses = connection.fetchall()

    # Handle filter request
    if request.method == 'POST':
        driver_id = request.form.get('driver_id')
        course_id = request.form.get('course_id')

        # Filter by driver
        # Select various details related to a driver's run on different courses.
        # Select the driver's ID.
        # Concatenate the driver's first name and surname to get the full name.
        # Select the course ID.
        # Select the course name.
        # Select the run number.
        # Select the time taken for the run in seconds.
        # If the number of cones is null, replace it with 0.
        # If the WD (withdrawal) is null, replace it with 0.
        # Calculate the total run time by adding the time taken, the penalty for cones, and the penalty for WD.
        # Assuming each cone adds 2 seconds and WD adds 10 seconds to the total time.
        # Start with the run table as the main table.
        # Join the driver table to get driver details.
        # Join the course table to get course details.
        # Filter the results to only include runs for a specific driver ID.
        # Order the results by driver ID, course name, and run number.

        if driver_id:
            connection.execute("""
SELECT 
    d.driver_id AS "Driver ID",
    CONCAT(d.first_name, ' ', d.surname) AS "Driver Name",
    c.course_id AS "Course ID",
    c.name AS "Course Name",
    r.run_num AS "Run Num",
    r.seconds AS "Time",
    COALESCE(r.cones, 0) AS "Cones",
    COALESCE(r.wd, 0) AS "WD",
    ROUND(r.seconds + COALESCE(r.cones, 0) * 2 + COALESCE(r.wd, 0) * 10,2) AS "Run Total"  -- Assuming each cone adds 2 seconds and WD adds 10 seconds
FROM 
    run r 
JOIN driver d ON r.dr_id = d.driver_id
JOIN course c ON r.crs_id = c.course_id
WHERE r.dr_id = %s
ORDER BY d.driver_id, c.name, r.run_num;
""", (driver_id,))
            #Filter by course
        elif course_id:
            # Retrieve details about drivers' runs on a specific course.
            # Get the driver's ID.
            # Concatenate the driver's first name and surname to form the full name.
            # Get the course ID.
            # Get the course name.
            # Get the run number for the driver on the course.
            # Get the time taken by the driver for the run in seconds.
            # If the number of cones hit during the run is null, replace it with 0.
            # If the WD (withdrawal) value is null, replace it with 0.
            # Calculate the total time for the run by adding the base time, penalty for hitting cones, and penalty for WD.
            # Assuming each cone hit adds 2 seconds and WD adds 10 seconds to the total time.
            # Start with the run table as the main table.
            # Join with the driver table to get details about the driver.
            # Join with the course table to get details about the course.
            # Filter the results to only include runs for a specific course ID.
            # Order the results by driver ID, course name, and run number.

            connection.execute("""SELECT 
    d.driver_id AS "Driver ID",
    CONCAT(d.first_name, ' ', d.surname) AS "Driver Name",
		c.course_id AS "Course ID",
    c.name AS "Course Name",
    r.run_num AS "Run Num",
    r.seconds AS "Time",
    COALESCE(r.cones, 0) AS "Cones",
    COALESCE(r.wd, 0) AS "WD",
    ROUND(r.seconds + COALESCE(r.cones, 0) * 2 + COALESCE(r.wd, 0) * 10,2) AS "Run Total"  -- Assuming each cone adds 2 seconds and WD adds 10 seconds
FROM run r 
JOIN driver d ON r.dr_id = d.driver_id
JOIN course c ON r.crs_id = c.course_id
where course_id = %s                              
ORDER BY d.driver_id, c.name, r.run_num;""", (course_id,))
            
        else:
            # Retrieve detailed information about each driver's runs across all courses.
            # Get the driver's ID.
            # Concatenate the driver's first name and surname to form the full name.
            # Get the course ID.
            # Get the course name.
            # Get the run number for the driver on the course.
            # Get the time taken by the driver for the run in seconds.
            # If the number of cones hit during the run is null, replace it with 0.
            # If the WD (withdrawal) value is null, replace it with 0.
            # Calculate the total time for the run by adding the base time, penalty for hitting cones, and penalty for WD.
            # Assuming each cone hit adds 2 seconds and WD adds 10 seconds to the total time.
            # Start with the run table as the main table.
            # Join with the driver table to get details about the driver.
            # Join with the course table to get details about the course.
            # Order the results by driver ID, course name, and run number.

            connection.execute("""SELECT 
    d.driver_id AS "Driver ID",
    CONCAT(d.first_name, ' ', d.surname) AS "Driver Name",
		c.course_id AS "Course ID",
    c.name AS "Course Name",
    r.run_num AS "Run Num",
    r.seconds AS "Time",
    COALESCE(r.cones, 0) AS "Cones",
    COALESCE(r.wd, 0) AS "WD",
    ROUND(r.seconds + COALESCE(r.cones, 0) * 2 + COALESCE(r.wd, 0) * 10,2) AS "Run Total"  -- Assuming each cone adds 2 seconds and WD adds 10 seconds
FROM 
    run r
JOIN driver d ON r.dr_id = d.driver_id
JOIN course c ON r.crs_id = c.course_id
ORDER BY d.driver_id, c.name, r.run_num;
""")

        runs = connection.fetchall()
    #If no filter is applied, show all runs  
    else:
        connection.execute("""SELECT 
    d.driver_id AS "Driver ID",
    CONCAT(d.first_name, ' ', d.surname) AS "Driver Name",
		c.course_id AS "Course ID",
    c.name AS "Course Name",
    r.run_num AS "Run Num",
    r.seconds AS "Time",
    COALESCE(r.cones, 0) AS "Cones",
    COALESCE(r.wd, 0) AS "WD",
    ROUND(r.seconds + COALESCE(r.cones, 0) * 2 + COALESCE(r.wd, 0) * 10,2) AS "Run Total"  -- Assuming each cone adds 2 seconds and WD adds 10 seconds
FROM 
    run r
JOIN driver d ON r.dr_id = d.driver_id
JOIN course c ON r.crs_id = c.course_id
ORDER BY d.driver_id, c.name, r.run_num;

""")
        runs = connection.fetchall()

    return render_template('edit_runs.html', drivers=drivers, courses=courses, runs=runs)


# define Apply edit button method for update edit runs
@app.route('/admin/update_run', methods=['POST'])
def update_run():
    connection = getCursor()

    driverid = request.form.get('driver_id')
    courseid = request.form.get('course_id')
    runnum = request.form.get('run_num')
    time = request.form.get('time')
    cones = request.form.get('cones')
    wd = request.form.get('wd')
    # update time cones wd in table run 
    connection.execute("UPDATE run SET seconds = %s, cones = %s, wd = %s WHERE dr_id = %s and crs_id = %s and run_num = %s", (time, cones, wd, driverid,courseid,runnum))

    return redirect(url_for('edit_runs'))


#define first step of method for adding a addriver
@app.route('/admin/add_driver', methods=['GET', 'POST'])
def add_driver():
    connection = getCursor()
    #retrive all cars's attributes from table car
    connection.execute("select * from car")
    cars = connection.fetchall()

    connection.execute("select driver_id,first_name,surname from driver where age is null or age >25")
    caregivers = connection.fetchall()

    if request.method == 'POST':
        # Handle the form submission here
        first_name = request.form.get('first_name')
        surname = request.form.get('surname')
        car_num = request.form.get('car_num')
        driver_type = request.form.get('driver_type')
        
        return render_template('add_driver_step2.html', first_name=first_name, surname=surname, car=car_num, driver_type=driver_type,caregivers=caregivers)

    return render_template('add_driver.html',cars=cars)

#define second step of method for adding a addriver
@app.route('/admin/finalize_driver', methods=['GET','POST'])
def finalize_driver():
    connection = getCursor()
    first_name = request.form.get('first_name')
    surname = request.form.get('surname')
    car = request.form.get('car')
    driver_type = request.form.get('driver_type')
    date_birth = request.form.get('dob')
    caregiver = request.form.get('caregiver')
    

    # A date in string format is converted to a datetime object
    specific_date = datetime.strptime(date_birth, '%Y-%m-%d') # type: ignore
    current_date = datetime.now()

    # Calculate the difference in the number of years between two dates
    years_difference = current_date.year - specific_date.year

    # If the current date is before the year of a particular date, subtract one year
    if (current_date.month, current_date.day) < (specific_date.month, specific_date.day):
                                                                                         years_difference -= 1

    if request.method == 'POST':
        if first_name and surname and car and driver_type == 'non_junior':
            sql = "INSERT INTO driver (first_name, surname,car) VALUES (%s, %s, %s)"
            val = (first_name,surname,car)
            connection.execute(sql, val)

            recordsql = """SET @new_driver_id = LAST_INSERT_ID();INSERT INTO run (dr_id, crs_id, run_num, seconds, cones, wd) 
VALUES 
(@new_driver_id, 'A', 1, NULL, NULL, 0),
(@new_driver_id, 'A', 2, NULL, NULL, 0),
(@new_driver_id, 'B', 1, NULL, NULL, 0),
(@new_driver_id, 'B', 2, NULL, NULL, 0),
(@new_driver_id, 'C', 1, NULL, NULL, 0),
(@new_driver_id, 'C', 2, NULL, NULL, 0),
(@new_driver_id, 'D', 1, NULL, NULL, 0),
(@new_driver_id, 'D', 2, NULL, NULL, 0),
(@new_driver_id, 'E', 1, NULL, NULL, 0),
(@new_driver_id, 'E', 2, NULL, NULL, 0),
(@new_driver_id, 'F', 1, NULL, NULL, 0),
(@new_driver_id, 'F', 2, NULL, NULL, 0);"""
            connection.execute(recordsql)
            return redirect(url_for('add_driver'))
        if first_name and surname and car and driver_type == 'junior_16_25' and date_birth:
            sql = "INSERT INTO driver (first_name, surname,car,date_of_birth,age) VALUES (%s, %s, %s, %s, %s)"
            val = (first_name,surname,car,date_birth,years_difference)
            connection.execute(sql, val)

            recordsql = """SET @new_driver_id = LAST_INSERT_ID();INSERT INTO run (dr_id, crs_id, run_num, seconds, cones, wd) 
VALUES 
(@new_driver_id, 'A', 1, NULL, NULL, 0),
(@new_driver_id, 'A', 2, NULL, NULL, 0),
(@new_driver_id, 'B', 1, NULL, NULL, 0),
(@new_driver_id, 'B', 2, NULL, NULL, 0),
(@new_driver_id, 'C', 1, NULL, NULL, 0),
(@new_driver_id, 'C', 2, NULL, NULL, 0),
(@new_driver_id, 'D', 1, NULL, NULL, 0),
(@new_driver_id, 'D', 2, NULL, NULL, 0),
(@new_driver_id, 'E', 1, NULL, NULL, 0),
(@new_driver_id, 'E', 2, NULL, NULL, 0),
(@new_driver_id, 'F', 1, NULL, NULL, 0),
(@new_driver_id, 'F', 2, NULL, NULL, 0);"""
            connection.execute(recordsql)
            return redirect(url_for('add_driver'))
        if first_name and surname and car and driver_type == 'junior_12_16' and date_birth and caregiver:
            sql = "INSERT INTO driver (first_name, surname,car,date_of_birth,age,caregiver) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (first_name,surname,car,date_birth,years_difference,caregiver)
            connection.execute(sql, val)

            recordsql = """SET @new_driver_id = LAST_INSERT_ID();INSERT INTO run (dr_id, crs_id, run_num, seconds, cones, wd) 
VALUES 
(@new_driver_id, 'A', 1, NULL, NULL, 0),
(@new_driver_id, 'A', 2, NULL, NULL, 0),
(@new_driver_id, 'B', 1, NULL, NULL, 0),
(@new_driver_id, 'B', 2, NULL, NULL, 0),
(@new_driver_id, 'C', 1, NULL, NULL, 0),
(@new_driver_id, 'C', 2, NULL, NULL, 0),
(@new_driver_id, 'D', 1, NULL, NULL, 0),
(@new_driver_id, 'D', 2, NULL, NULL, 0),
(@new_driver_id, 'E', 1, NULL, NULL, 0),
(@new_driver_id, 'E', 2, NULL, NULL, 0),
(@new_driver_id, 'F', 1, NULL, NULL, 0),
(@new_driver_id, 'F', 2, NULL, NULL, 0);"""
            connection.execute(recordsql)
            return redirect(url_for('add_driver'))


    return render_template('add_driver_step2.html', first_name=first_name, surname=surname, car=car, driver_type=driver_type)


