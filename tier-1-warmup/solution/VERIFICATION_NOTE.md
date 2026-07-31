**1. What the AI got wrong (or almost wrong):**
- The first time I tried to create the PROMPT_LOG it just duplicate the file.
- There was different error scenarios that were not handled correctly.

**2. How I caught it:**
- I see the same file as the template.
- The code was failing to identify the whitespace only rows, and failed when I added more headers on the CSV file.

**3. How I confirmed the final result is correct**
- I take out the instructions for the log and put it directly.
- I create unit test for each scenario and also made changes on the CSV file to add extra test cases.
