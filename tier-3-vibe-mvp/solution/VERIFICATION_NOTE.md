# Verification Note

> 5–8 lines. Honesty is graded; "the AI made no mistakes" is almost never true and reads as a red flag.

**1. What the AI got wrong (or almost wrong):**
- I got two major incidents during this process. 
    - When I start creating the base, the dependencies were outadted, and there was a lot of vulnerabilities, so I need to update the dependencies.
    - As I used 2 different agents to create the app, there was some inconsistencies in the code, so I need to refactor the code to make it consistent. 
**2. How I caught it:**
- I caught these issues by following the instructions in the prompt and the rubric. 
    - The vulnerabilities were caught by running `npm audit` command. 
    - The inconsistencies in the code were caught by running `npm run lint` command.
**3. How I confirmed the final result is correct** (tests run, manual checks, sample data used):
- Validating the vulnerabilities are gone.
- I confirmed the final result is correct by running the tests and checking the manual checks. 
