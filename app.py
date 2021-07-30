#!/usr/bin/env python3
from aws_cdk import (
    core
)


class BopmCdkStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


app = core.App()
BopmCdkStack(app, "BopmCdkStack")
app.synth()
