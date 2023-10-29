# BRMMWebApp
This WebApp is for Lincoln University assessment only

# Report

Your report must be created using GitHub Markdown format and saved in the `README.md` file of your GitHub repository. It does not need to be a formal report – a tidy document using the following headings will be sufficient. Write a brief project report that includes:

## Web Application Structure

- **Outline of the Structure:** 
    - Outline the structure of your solution (routes & functions, and templates). This should be brief and can be text-based or a diagram (as an image).
    -`[My Answer]:`![Websites_route](https://github.com/AnnieDJ/image-in-readme/assets/146434944/8370d267-5c1c-402e-a346-afb46aeefb43)

## Assumptions and Design Decisions

- **Assumptions:**
    - Detail any assumptions that you made (what isn't clear or stated in this brief that you had to assume or ask about).
    - Discuss the design decisions you made when designing and developing your app (what 
design options you weighed up, why you designed your app the way that you did, your 
decisions about the routes, templates, navigation, broad layout, etc, that you made).
    - `[My Answer]:`
- I'd like to create links on the home page to "List of courses," "Driver's run details," "List of drivers," "Overall results," and "Bar graph." Additionally, there should be an "Admin" link. When you click on the "Admin" link, it should take you to the "AdminHome" page. On this page, you'll find links to four main functions for the admin: "Junior driver list," "Driver search," "Edit runs," and "Add driver."

- In my web application (App), I handle SQL-related logic in app.py. This includes adding drivers, querying driver data, retrieving driver details, fetching data on junior drivers, getting the list of courses, fetching overall results, and modifying run records. In the "templates" folder, I store various Jinja web templates used to display database-related fields. When necessary, I use CSS to style the components. When writing the code, I consider that some web pages have both POST and GET requests, so I handle them separately. Sometimes, there are multiple dropdowns, so I pass multiple parameters to app.py and identify them by name. In some web pages with multiple steps, such as the "Add driver" page, there is a need to pass data between web pages. In some SQL queries, I utilize special functions like Common Table Expressions, Case, COALESCE, etc.

- In the regular user interfaces (corresponding to "List of courses," "Driver's run details," "List of drivers," "Overall results," and "Bar graph"), I reuse the "base.html" template. However, in the admin interface (corresponding to "Junior driver list," "Driver search," "Edit runs," and "Add driver"), I don't reuse the "adminmain" template. This is because in the admin interface, clicking the "Home" button returns to the website's main page. In contrast, in the pages for "Junior driver list," "Driver search," "Edit runs," and "Add driver," clicking the "Home" button takes you back to the Admin homepage.
    
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