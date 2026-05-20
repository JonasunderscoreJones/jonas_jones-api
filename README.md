# jonas_jones-api

API supporting the Jonas_Jones project and data infrastructure.

## Installation

As of now, the project has no proper production build and unless the proper environment variables are set, the API will not work.


Clone the repository and install the dependencies.
```bash
pip install -r requirements.txt
```

## Usage

To run the API, simply run the following command.
```bash
python main.py runserver
```
## Roadmap (outdated)

- analytics backend. track request origin through IP from header (store IP hash, region and time)
- rewrite all scripts in rust
- DB implementation for projects, kcomebacks, minecraft mod versions
- session backend, auth token system
- implementation for dashboard front-end with analytics/config
- complete minecraft mod implementation

More updated Roadmap will follow (currently exists in my Notes)