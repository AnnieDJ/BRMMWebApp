# BRMMWebApp
This WebApp is for Lincoln University assessment only

# Report

Your report must be created using GitHub Markdown format and saved in the `README.md` file of your GitHub repository. It does not need to be a formal report – a tidy document using the following headings will be sufficient. Write a brief project report that includes:

## Web Application Structure

- **Outline of the Structure:** 
    - Outline the structure of your solution (routes & functions, and templates). This should be brief and can be text-based or a diagram (as an image).
    -`[My Answer]:`![WebsiteRoute](https://github.com/AnnieDJ/image-in-readme/assets/146434944/a83fd5b7-8042-461b-a2a3-fa6ba47c8ca6)

## Assumptions and Design Decisions

- **Assumptions:**
    - Detail any assumptions that you made (what isn't clear or stated in this brief that you had to assume or ask about).
    - Discuss the design decisions you made when designing and developing your app (what 
design options you weighed up, why you designed your app the way that you did, your 
decisions about the routes, templates, navigation, broad layout, etc, that you made).
    - `[My Answer]:`
I want to create links on the home page to List of courses, Driver’s run details, List of drivers, Overall results, and Bar graph. Additionally, there is an Admin link that, when clicked, leads to the AdminHome page. In this page, there are four links: Junior driver list, Driver search, Edit runs, and Add driver, which correspond to the functions for the Admin.In my web application, I handle SQL-related logic in app.py, which includes adding a driver, querying driver data, fetching driver details, querying Junior Drivers, retrieving the Course List, obtaining overall results, and modifying run records. The templates folder stores various Jinja web templates used to display database-related fields, and CSS is applied when necessary to style the elements. During development, I considered that some web pages support both POST and GET requests, so I handled them separately. In certain cases, there are multiple dropdown menus, resulting in multiple parameters sent to app.py, which are distinguished by their names. Some web pages involve multiple steps, such as the Add Driver page, where data needs to be passed between pages. In some SQL queries, I utilized special functions like Common Table Expression, Case, and COALESCE for data retrieval.In the standard pages (List of courses, Driver’s run details, List of drivers, Overall results, and Bar graph), I reused the base.html template. In the Admin pages (Junior driver list, Driver search, Edit runs, and Add driver), I utilized the adminmain.html template.
    
## Database Questions

Refer to the supplied `motorkhana_local.sql` file to answer the following questions:

- **Car Table Creation:**
    - What SQL statement creates the car table and defines its three fields/columns? (Copy and paste the relevant lines of SQL.)
    - `[My Answer]:`CREATE TABLE IF NOT EXISTS car
(
car_num INT PRIMARY KEY NOT NULL,
model VARCHAR(20) NOT NULL,
drive_class VARCHAR(3) NOT NULL
);
- **Relationship Setup:**
    - Which line of SQL code sets up the relationship between the car and driver tables?
    - `[My Answer]:`FOREIGN KEY (car) REFERENCES car(car_num)
ON UPDATE CASCADE
ON DELETE CASCADE
- **Data Insertion:**
    - Which 3 lines of SQL code insert the Mini and GR Yaris details into the car table?
    - `[My Answer]:`INSERT INTO car VALUES ('ABC123', 'Mini Cooper', 'FWD');
INSERT INTO car VALUES ('XYZ789', 'Toyota GR Yaris', 'AWD');
- **Default Value Setting:**
    - Suppose the club wanted to set a default value of ‘RWD’ for the `driver_class` field. What specific change would you need to make to the SQL to do this? (Do not implement this change in your app.)
    - `[My Answer]:`driver_class CHAR(3) NOT NULL DEFAULT 'RWD'
- **Login Implementation:**
    - Suppose logins were implemented. Why is it important for drivers and the club admin to access different routes? As part of your answer, give two specific examples of problems that could occur if all of the web app facilities were available to everyone.
    - `[My Answer]:`Example 1: If all facilities were available to everyone, a regular driver could accidentally or maliciously delete or modify other drivers' data, leading to data loss or corruption.
Example 2: Without proper access controls, confidential information, such as financial data or personal details, could be exposed to unauthorized users, leading to potential privacy breaches.