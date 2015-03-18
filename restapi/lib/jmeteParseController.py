# -*- coding: utf-8 -*-

def parseJMeterParam(m_config):

        #获取参数
        dctMachineParam =m_config["dctMachineParam"]
        dctCaseScenario = m_config["dctCaseScenario"]
        dctJMeterParam = m_config["dctJMeterParam"]
        dctToolParam = m_config["dctToolParam"]
        #获取细化参数
        sToolPath = dctToolParam["sToolPath"]
        bNeedToolLog = dctToolParam["bNeedToolLog"]
        sToolLogPath = dctToolParam["sToolLogPath"]
        sCaseScriptPath = dctCaseScenario["sCaseScriptPath"]
        nCaseRunType = dctCaseScenario["nCaseRunType"]
        bSetAggregateLogPath = dctToolParam["bSetAggregateLogPath"]
        sAggregatePath = dctToolParam["sAggregatePath"]

        sJMeterParamPrefix = "J"
        sRunTypeParam = ""

        if nCaseRunType == 602:
            sRunTypeParam = " -R"
            lstJMeterServer = dctMachineParam["lstJMeterServer"]
            sJMeterServerParam = ""
            for sJMeterServer in  lstJMeterServer:
                if  sJMeterServerParam == "":
                    sJMeterServerParam = sJMeterServer
                else:
                    sJMeterServerParam = sJMeterServerParam + "," + sJMeterServer
            sRunTypeParam = sRunTypeParam + " " + sJMeterServerParam
            sJMeterParamPrefix = "G"
        elif nCaseRunType == 603:
            sRunTypeParam = " -r"
            sJMeterParamPrefix = "G"

        lstJMeterParamKey = dctJMeterParam.keys()

        sJMeterParam=""
        for jmeterParamKey in lstJMeterParamKey:
            sJMeterParam = sJMeterParam + " -" + sJMeterParamPrefix + jmeterParamKey + "=" +  str(dctJMeterParam[jmeterParamKey])


        sToolLogParam = ""
        if bNeedToolLog:
            sToolLogParam = ' -l "{0}"'.format(sToolLogPath)

        sAggregateLogParam = ""
        if bSetAggregateLogPath:
            sAggregateLogParam = ' -JAGRPT="{0}"'.format(sAggregatePath)

        sCommand = sToolPath + " -n" + sRunTypeParam + " -t " + "\"sCaseScriptPath\"" + sJMeterParam + sToolLogParam + sAggregateLogParam

        return sCommand
