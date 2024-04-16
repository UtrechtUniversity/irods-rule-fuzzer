'''Contains functions for interacting with rules in Yoda
'''
from io import StringIO

from irods.rule import Rule


def call_rule(session, rulename, params, number_outputs,
              rule_engine):
    """Run a rule

       :param rulename: name of the rule
       :param params: dictionary of rule input parameters and their values
       :param number_output: number of output parameters
       :param rule_engine: rule engine to run rule on
     """
    body = 'myRule {{\n {} ('.format(rulename)

    for input_var in params.keys():
        body += "*{},".format(input_var)

    outparams = list(
        map(lambda n: '*outparam{}'.format(str(n + 1)), range(number_outputs)))
    body += '{}); writeLine("stdout","{}")}}'.format(
        ",".join(outparams),
        "\n".join(outparams))

    input_params = {"*{}".format(k): '"{}"'.format(v)
                    for (k, v) in params.items()}
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

    return buf[:number_outputs]
