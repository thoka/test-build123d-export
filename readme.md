Trying out the CAD-as-code tool build123d.

## Current questions

- [x] Which python versions are supported?
- [ ] Which features (labels, colors) survive export?

## Results

### Supported Python versions
The newest compatible version is 3.13. 3.12 also works. 3.14 and 3.15 are currently not supported.

### build123d export feature matrix (latest run)

Run: /home/toka/dv/build123d/.venv/bin/python test-digits.py  
Date: 2026-01-13T17:32:16

Generated the digits exports and inspected them for hierarchy names and colors.

| Format  | File    | root  | child   | text  | box  | colors |
|:-------|:-------|:-----|:--------|:-----|:----|:-------|
| step    | ok      | yes   | yes     | -     | -    | - |
| stl     | ok      | -     | -       | -     | -    | - |
| 3mf     | ok      | -     | -       | -     | -    | - |
| bin     | ok      | -     | -       | -     | -    | - |
| brep    | ok      | -     | -       | -     | -    | - |
| gltf    | ok      | -     | -       | -     | -    | - |

### CadQuery export feature matrix (latest run)

Run: /home/toka/dv/build123d/.venv/bin/python cq-test-digits.py  
Date: 2026-01-13T17:32:16

Generated the digits exports and inspected them for hierarchy names and colors.

| Format  | File    | root  | child   | text  | box  | colors |
|:-------|:-------|:-----|:--------|:-----|:----|:-------|
| step    | ok      | yes   | yes     | yes   | yes  | yes |
| stl     | ok      | -     | -       | -     | -    | - |
