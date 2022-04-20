# Documentation

## Navigating Concerto

This section will provide the necessary information to equip users to navigate the Concerto platform. The Concerto platform consists of 7 tabs and this section will break down each individual tab and its functionality.

## 1.1 Tests

This is the brain of your web app. Any given test can take a set of input parameters, perform a set of tasks and then output a set of return variables. These three components are described in detail below as Test Inputs, Test Logic and Test Outputs respectively.

## 1.2 Test Wizards

This tab allows the user to define more complex input methods for each parameter

value but are otherwise cosmetic in nature, allowing you to simplify and save time in complex applications that reuse many of the same functions.

## 1.3 Templates

Templates are pages that will be shown to users during the test execution. Everything that the user sees in their browser window during the test can be determined at the template level. We call them templates because most pages will accept parameters from the test logic and change their look depending on the value of these parameters.

## 1.4 Data Tables

This section of Concerto stores data Tables. Data tables can be used to store anything from test item responses to file paths to demographic information. Each data table has a corresponding table in the MySQL database server.

## 1.5 Files

The Files tab allows you to manage images, documents and any other assets that your test may need to use which are not handled within the tests, data tables or templates sections. It is your library of global, publicly accessible files that can be used anywhere – from your templates to test logic.

## 1.6 Users

The Users tab in the Concerto administration panel is used to determine who has access to that Concerto instance, in other words who can create or edit test content. Users is used in this sense in these guides and is unrelated to any participants that may have completed a test.

## 1.7 Administration

The Administration tab in the Concerto panel contains several sections that can be helpful in monitoring aspects of your Concerto environment. These are explained below.

## Creating a New Grouped Assessment Test

When creating a new Grouped Assessment test there are a few things that must be done in order to ensure that the system works as intended. The first of which is makes sure that the users are authorized under the correct set of users. That is done in the Authorize User Block (See Authorize User Below). Next, the questions must be pulled in from the correct Data Table (See Grouped Questions Below).

AuthorizeUser:

After test start the program must authorize that the intended user is taking the correct test. This is done using the Concerto Authorize User block. To ensure that this block is working correctly, simply navigate to the Data Table tab under the block and select the table of users you would like to use to authenticate.

![Screen Shot 2022-02-04 at 8.37.36 AM.png](docimg/Screen_Shot_2022-02-04_at_8.37.36_AM.png)

Questions Data Table:

When running a test it is imperative to ensure that the questions are being pulled from the correct data table location. To make sure that this is the case simply navigate to the Items-Table tag under the groupedAssesment2 block and make sure that the Table-Table is pulling from the correct Data Table.

Quick Debug:

When creating a new test using the groupedAssesment2 block, it is imperative to know that if the test encounters a problem after user authentication, the test might not have 2 of the variables that it needs to process. They might not be initialized. Instead locate the Item Bank Extra Fields - list elements tab under the groupedAssesment2 block and add those variables. Then the code will be able to run effectively. (See below)

![Untitled](docimg/Untitled.png)

### Custom R Code

If it becomes necessary for any reason that the user should have to execute custom R code in order to calculate and processor certain things it is seemingly difficult but quite simple knowing the correct circumstances.

First of all, using the eval block that is built into Concerto the user can evaluate and pass in different variables in order to evaluate that node. For example see the below images

![Untitled](docimg/Untitled%201.png)

![Untitled](docimg/Untitled%202.png)

## GUI For Converting BlackBoard Test to Concerto

### Dependencies and Software Specification

The Graphical User Interface is built upon Python 3 utilizing the “Less is More” methodology of making the most streamlined workspace for the user.

This Application takes in a folder downloaded from blackboard test export and formats it for import into the concerto adaptive testing framework. The user will select a folder for upload and then let the application run its magic! Simple as that.

This is the requirements.txt that defines the packages required for the python Application

```
numpy==1.21.4
pandas==1.3.4
PySimpleGUI==4.55.1
python-dateutil==2.8.2
pytz==2021.3
six==1.16.0
xmltodict==0.12.0
```

![Screen Shot 2022-04-13 at 4.28.28 PM.png](docimg/Screen_Shot_2022-04-13_at_4.28.28_PM.png)

![Screen Shot 2022-04-13 at 4.28.59 PM.png](docimg/Screen_Shot_2022-04-13_at_4.28.59_PM.png)

## Executing custom R code

This process is actually incredibly easy and can be done in just a couple of steps.
First of all you are going to want to import the “Eval” block into your workflow as shown below

![Screen Shot 2022-03-02 at 3.25.11 PM.png](docimg/Screen_Shot_2022-03-02_at_3.25.11_PM.png)

You can then specify any specific inputs and outputs that you want by clicking on the blue and red output buttons.

![Screen Shot 2022-03-02 at 3.26.07 PM.png](docimg/Screen_Shot_2022-03-02_at_3.26.07_PM.png)

Finally simply click on the word eval and type out custom R code into the eval block

![Screen Shot 2022-03-02 at 3.26.36 PM.png](docimg/Screen_Shot_2022-03-02_at_3.26.36_PM.png)

There you go 🙂 done and done

## Displaying TraitTheta and Theta

The first thing to do here is to take the groupedAssesment2Node and add a couple of output pieces by clicking the red plus sign. Pictured here:

![Untitled](docimg/Untitled%203.png)

![Untitled](docimg/Untitled%204.png)

You’ll then want to connect those via line connection to an eval block to do a little bit of code manipulation. You will click the blue plus button on that eval block and input the traitTheta and theta dynamic input variables. Ignore everything else for now we will discuss the important parts further down.

![Untitled](docimg/Untitled%205.png)

Next you will create one more eval block and do the same thing with some custom output in order to initialize the intercept and the slope for your theta calculations.

![Untitled](docimg/Untitled%206.png)

![Untitled](docimg/Untitled%207.png)

Next you’ll go ahead and connect those to the previously created eval block along with two more dynamic input variables called intercept and slope.

![Untitled](docimg/Untitled%208.png)

Then we are going to run a bit of code laid out below within that eval block. You will get to this by clicking on the blue ‘eval’ name on the top of the block.

Here is that code:

```r
toReturn = "";
toReturn = paste("Your'e overall score for this test is a ", ((theta * slope + intercept) * 100), "% <br><br>");
for (i in 1:length(traitSem)) {
  toReturn = paste(toReturn, "Trait name: ", names(traitSem)[i]);
  toReturn = paste(toReturn, " with a score of: ", ((traitSem[[i]] * slope + intercept) * 100.0), "% for this question <br>");
}
```

Go ahead and past that into the code - R code area and then we can move onto the final step.

Create another dynamic output on that eval block called “toReturn” it is very important that it has that exact name with the same capitalization.

Then create a showPage block and connect the logical flow of the test to it after the eval block as well as connecting the previous toReturn variable to a new dynamic input variable on the showPage called “toReturn”.

![Untitled](docimg/Untitled%209.png)

Finally edit the content area of the showPage with whatever HTML you would like to show to your test takers and you’ll be on your way 🙂. (to show the toReturn variable simply put {{toReturn}} anywhere in the html code)

Attached here is the html that we are using to show you how to do that.

```html
Congratulations, you have completed the test! Your professor will work on calculating the grade once everyone has completed their test. Have a nice day!
Thank you for participating in the test. Your scores are as follows: 

{{toReturn}}
```

Attached below as well is a full image of our workflow to give you an idea of the setup for displaying to the test takers. Hope this helps 😃 - CATT Team

![Untitled](docimg/Untitled%2010.png)
