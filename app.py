#!/usr/bin/env python3
from aws_cdk import (
    aws_lambda,
    aws_lambda_python,
    aws_apigateway,
    core
)


class BopmCdkStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bopm_lambda = aws_lambda_python.PythonFunction(
            self,
            id='lambda',
            function_name='BopmLambda',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            timeout=core.Duration.seconds(60),
            memory_size=512,
            entry='./bopm_cdk/bopm',
            handler='handler',
            index='bopm_lambda.py'
        )

        api = aws_apigateway.LambdaRestApi(
            self,
            id='lambda-apigateway',
            handler=bopm_lambda
        )

app = core.App()
BopmCdkStack(app, "BopmCdkStack")
app.synth()
