# matrix_interpolator

# User Story

As a data analyst, I can call a command-line tool that accepts a 
two-dimensional matrix as input and produces an output matrix with the same 
dimensions in which missing values have been interpolated as the average of all 
non-diagonal neighbouring values. 

# Task

Create a production quality software tool to implement the above user story. 

We have spoken to the user representative and they agreed that the initial task 
should be to focus on core functionality, so we have refined the functional 
requirements to a limited set which should provide them with a minimum viable 
product: 
  - Input is in the form of a comma-separated file (CSV) in which rows are 
    separated by newline characters and the value of each column within a row 
    is separated by a comma.
  - Missing values in the input are encoded as `nan`.
  - Output is in the same form as the input, and have the same number of rows 
    and columns, but should contain no missing values.
  - Missing values should be interpolated as the average of all neighbouring 
    non-diagonal values.
  - Values that are non-missing in the input should be preserved in the output 
    without change.

Our user representative have also provided a tiny example of input and output 
data files and we have included these in the 'example_data' directory.

The tool should be developed with acceptance and unit tests that would aid 
further collaborative development. Please use whatever language(s) you feel are 
most appropriate for this task, considering both what you are comfortable using 
and what would be the easiest for the team to continue to develop and maintain. 
At a minimum, include a README.md file that specifies how to run the code 
(including required versions of compiler/interpreter and how to install any 
required dependencies).

The purpose of this task is for you to showcase your approach to software 
development. Please do not spend more than three hours on this task.

# Extra

If you complete the task in less than three hours, consider adding the following 
additional requirements in the remaining time:
  - Exit gracefully and with user-friendly error messages when malformed input is
    provided.
  - Handle adjacent missing values (the choice of how to interpolate in this 
    case is left to you).
