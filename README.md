## Solution description:

Given software solution automatically extracts and contextualizes entities from provided scientific paper PDFs.
Data is processed and returned via an API endpoint.

The objective is to develop a simple software API endpoint that is capable of automatically extracting
and contextualizing entities from the supplied scientific paper PDFs. This system should be able to semantically
identify and interpret the key information contained within these documents, regardless of their complexity. 
Key components:
- PDF Parsing;
- API call handling;
- Semantic extraction of entities;
- Filtering for entities relevant to the domain.

**This solution was tested on Mac M1. If you run with package incompatibitily problem, please reach out to me and I will
build a Docker container.**

## Instructions to run the solution:
- Make sure that python is installed;
- Run build.sh file to initialise virtual environment, install dependancies ans start the local server;
- Run test_api.sh to use provided test files from the Programming Challenge Files directory as the API input.
- If you want to run the API on another .pdf file, use this command:
- **curl -X POST http://localhost:5000/api/v1/extract -F "file=@${path_to_your_file}"**