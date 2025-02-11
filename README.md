# nusearch

An AI Research Agent for Northwestern University Libraries.

## Installation

```bash
pip install nusearch
```

## Authentication

Before using nusearch, you need to authenticate with AWS SSO:

```bash
export AWS_PROFILE=your-profile-name
aws sso login
```

## Usage

To start the nusearch server:

```bash
nusearch
```

This will start a server on http://0.0.0.0:8000/

## Description

nusearch is an AI-powered research assistant designed specifically for Northwestern University Libraries. It provides an interface to interact with library resources and perform research tasks.

## Features

- AI-assisted research queries
- Integration with Northwestern University Libraries resources
- Web interface accessible via browser

## Requirements

- Python 3.11+
- pip package manager
- AWS CLI configured with SSO access

## License

Copyright © Northwestern University Libraries

