# Exam monitoring — Code Structure

## Main Application Files

- **app.py**
  - server part
  - handle all routs
  - include session generation mechanics


- **cy_frame.pyx**
  - additional image processing
  - checking for the presence of the student in the frame  
  <sub>the file is optimized using `cython`</sub>


- **setup.py**
  - using for building the cython file



- templates/**login.html**/
  - login page logic and interface


- templates/**session.html**/
  - handling general session logic
    - chat functionality
    - teacher page
    - student page
  - interface for teacher and student session pages

- templates/**student_dashboard**/
  - interface for student login page


- templates/**teacher_dashboard**/
  - interface for teacher login page

---

# Secondary Files

- static/ (**all .css files**)
  - styling for corresponding html.files


- static/**Video1_fixed.mp4**
  - background video for login, student login & teacher login pages

- static/Images/**Untitled1.png**
  - background image for the session page (student and teacher)

---

# Data files
    
- server log
  - logs all actions on the server

---

# Example Data Structure
```log
2025-09-04 20:41:09 [INFO] Server started
```
```log
2025-09-04 20:41:25 [ERROR] The client is using an unsupported version of the Socket.IO or Engine.IO protocols (further occurrences of this error will be logged with level INFO)
```
```log
2025-09-04 20:41:47 [WARNING] [VIOLATION] Face is not detected for John
```
