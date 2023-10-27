# BRMMWebApp
This WebApp is for Lincoln University assessment only

# Report

Your report must be created using GitHub Markdown format and saved in the `README.md` file of your GitHub repository. It does not need to be a formal report – a tidy document using the following headings will be sufficient. Write a brief project report that includes:

## Web Application Structure

- **Outline of the Structure:** 
    - Outline the structure of your solution (routes & functions, and templates). This should be brief and can be text-based or a diagram (as an image).
    -[My Answer]:![Websites](https://github.com/AnnieDJ/image-in-readme/assets/146434944/940be879-dc80-497b-b353-69a2e255d8d2)

## Assumptions and Design Decisions

- **Assumptions:**
    - Detail any assumptions that you made (what isn't clear or stated in this brief that you had to assume or ask about).
    - A:What I want to create is that If I have time,I want to add some functions to check out wheather the admin himself do the admin work.
    - I like to add some new brands of cars for people to pick up.
    - 
- **Design Decisions:**
    - Discuss the design decisions you made when designing and developing your app (what design options you weighed up, why you designed your app the way that you did, your decisions about the routes, templates, navigation, broad layout, etc, that you made).
    - Note your assumptions and your decisions as you work, so you do not forget them! For example, did you use multiple similar pages, or share some page templates perhaps with hidden items? Did you use GET or POST to request and send data, and how and why? You will have considered many design possibilities. These are only two examples.

## Database Questions

Refer to the supplied `motorkhana_local.sql` file to answer the following questions:

- **Car Table Creation:**
    - What SQL statement creates the car table and defines its three fields/columns? (Copy and paste the relevant lines of SQL.)
    - [My Answer]:CREATE TABLE IF NOT EXISTS car
(
car_num INT PRIMARY KEY NOT NULL,
model VARCHAR(20) NOT NULL,
drive_class VARCHAR(3) NOT NULL
);
- **Relationship Setup:**
    - Which line of SQL code sets up the relationship between the car and driver tables?
    - [My Answer]:FOREIGN KEY (car) REFERENCES car(car_num)
ON UPDATE CASCADE
ON DELETE CASCADE
- **Data Insertion:**
    - Which 3 lines of SQL code insert the Mini and GR Yaris details into the car table?
    - [My Answer]:INSERT INTO car VALUES ('ABC123', 'Mini Cooper', 'FWD');
INSERT INTO car VALUES ('XYZ789', 'Toyota GR Yaris', 'AWD');
- **Default Value Setting:**
    - Suppose the club wanted to set a default value of ‘RWD’ for the `driver_class` field. What specific change would you need to make to the SQL to do this? (Do not implement this change in your app.)
    - [My Answer]:driver_class CHAR(3) NOT NULL DEFAULT 'RWD'
- **Login Implementation:**
    - Suppose logins were implemented. Why is it important for drivers and the club admin to access different routes? As part of your answer, give two specific examples of problems that could occur if all of the web app facilities were available to everyone.
    - [My Answer]:Example 1: If all facilities were available to everyone, a regular driver could accidentally or maliciously delete or modify other drivers' data, leading to data loss or corruption.
Example 2: Without proper access controls, confidential information, such as financial data or personal details, could be exposed to unauthorized users, leading to potential privacy breaches.