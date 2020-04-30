#!/usr/bin/env python3

import json

def lambda_handler(event, context):
    print(json.dumps(event))
    return event
