'''Contains functions for interacting with rules in Yoda
'''
from io import StringIO

from irods.rule import Rule


def call_rule(session, rulename, params, number_outputs,
              rule_engine):
    """Run a rule

       :param rulename: name of the rule
       :param params: dictionary of rule input parameters and their values
       :param number_output: number of output parameters, or None to return all parameters
       :param rule_engine: rule engine to run rule on
     """
    body = _construct_rule_body(params, number_outputs, rulename)

    input_params = _construct_input_params(params)
    output_params = 'ruleExecOut'

    re_config = {'instance_name': rule_engine} if rule_engine is not None else {}

    myrule = Rule(
        session,
        rule_file=StringIO(body),
        params=input_params,
        output=output_params,
        **re_config)

    outArray = myrule.execute()
    buf = outArray.MsParam_PI[0].inOutStruct.stdoutBuf.buf.decode(
        'utf-8').splitlines()

    return buf if number_outputs is None else buf[:number_outputs]


def _construct_rule_body(params, number_outputs, rulename):
    body = 'myRule {{\n {} ('.format(rulename)

    for input_var in params.keys():
        body += "*{},".format(input_var)

    if number_outputs is None or number_outputs == 0:
        if len(params.keys()) > 0:
            body = body[:-1]
        outparams = list(
            map(lambda n: '*outparam{}'.format(str(n + 1)), range(len(params.keys()))))
        body += ');\n writeLine("stdout","{}");}}'.format(
            "\n".join(map(lambda n: "*" + n, params)))
    else:
        outparams = list(
            map(lambda n: '*outparam{}'.format(str(n + 1)), range(number_outputs)))
        body += '{});\n writeLine("stdout","{}");}}'.format(
            ",".join(outparams),
            "\n".join(outparams))

    return body


def _construct_input_params(params):
    return {"*{}".format(k): '"{}"'.format(v)
            for (k, v) in params.items()}
