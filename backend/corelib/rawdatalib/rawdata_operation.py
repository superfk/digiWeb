import os
import json
import pyAesCrypt
import hashlib


dummy_raw_data = {
    'stepName': 'HDNS', 
    'rawData': [79.2, 79.5, 79.5], 
    'tagsResult': [
        {
            'tagName': 'median',
            'result': 79.5, 
            'unit': ' ', 
            'compareResult': {
                'comparePass': 'FAIL', 
                'roundedData': 79.5, 
                'roundedLSL': 79.6, 
                'roundedUSL': 79.8, 
                'compareType': 'IN_RANGE', 
                'compareToDecimal': 1
                }
        }, 
        {
            'tagName': 'max', 
            'result': 79.5, 
            'unit': ' ', 
            'compareResult': {
                'comparePass': 'FAIL', 
                'roundedData': 79.5, 
                'roundedLSL': 79.6, 
                'roundedUSL': 79.8, 
                'compareType': 'IN_RANGE', 
                'compareToDecimal': 1
                }
        }
    ], 
    'overallStatus': 'PASS', 
    'stepStatus': 'INIT', 
    'startProcessT': 1598838401.8667703, 
    'endProcessT': 1598838401.8667703, 
    'exeProcessT': 0, 
    'startSampleT': 1598838401.9271183, 
    'endSampleT': 1598838436.1493602, 
    'exeSampleT': 34.22224187850952, 
    'startPointT': 1598838424.7396593, 
    'endPointT': 1598838436.1493602, 
    'exePointT': 11.409700870513916, 
    'prograss': 0, 
    'sampleIndex': 0, 
    'sampleID': 0, 
    'batch_uuid': '251d3-d1c0-1b4f-7a1f-601a8c6da7c', 
    'batch_name': 'test', 
    'compound_id': 4, 
    'test_plan_id': 6
}

class Property(object):
    def __init__(self, name, value, datatype) -> None:
        self.name = name
        self.value = value
        self.type = datatype
    def to_dict(self):
        return {'name': self.name, 'value': self.value, 'type': self.type}

class Batch(object):
    def __init__(self, batchId, batchName):
        self.batchId = batchId
        self.batchName = batchName
        self.properties = []
        self.testItems = []
    def to_dict(self):
        return {'batchId': self.batchId, 'batchName': self.batchName, 'properties':self.properties, 'testItems':self.testItems}

class TestItem(object):
    def __init__(self, name):
        self.name = name
        self.properties = []
        self.datasets = []
    def to_dict(self):
        return {'name': self.name, 'properties':self.properties, 'dataset':self.datasets}

class Dataset(object):
    def __init__(self, name):
        self.name = name
        self.data = []
        self.properties = []
    def to_dict(self):
        return {'name': self.name, 'properties':self.properties, 'data':self.data}

class Data:
    def __init__(self, xdata=[], ydata=[]) -> None:
        self.xdata = xdata
        self.ydata = ydata
    def to_dict(self):
        return {'xdata': self.xdata, 'ydata':self.ydata}

class ScalerArrayData(Data):
    def __init__(self,data=[]) -> None:
        super().__init__([],data)

class TimeArrayData(Data):
    def __init__(self,time=[], data=[]) -> None:
        super().__init__(time,data)


class DataManager(object):
    def __init__(self, sessionUuid):
        self.sessionUuid = sessionUuid
        self.batches = [] # {'batchUuid1':{}, 'batchUuid2': {}, ...}
        
    def clear_records(self):
        self.batches = []
    
    def clean_data(self, rawData):
        cleaned_data = rawData.copy()
        del cleaned_data['prograss']
        del cleaned_data['stepStatus']
        del cleaned_data['batch_uuid']
        del cleaned_data['batch_name']
        del cleaned_data['compound_id']
        del cleaned_data['test_plan_id']
        return cleaned_data
    
    def add_records(self, rawData, exportFolderPath):
        # get batch info
        currentBatchUuid = rawData['batch_uuid']
        currentBatchName = rawData['batch_name']
        currentCompId = rawData['compound_id']
        currentTestPlanId = rawData['test_plan_id']
        currentSampleId = rawData['sampleID']
        # clean data
        cleaned_data = self.clean_data(rawData)
        # check if data file existed
        batchFolder = os.path.join(exportFolderPath, 'testData', currentBatchName)
        sampleFilepath = os.path.join(batchFolder, currentSampleId)
        if not os.path.exists(batchFolder):
            os.makedirs(batchFolder)
        
        foundBatch = False
        for batch in self.batches:
            if currentBatchUuid == batch['batch_uuid']:
                batch['samples'].append(cleaned_data)
                foundBatch = True
        if not foundBatch:
            newBatch = {}
            newBatch['batch_uuid'] = currentBatchUuid
            newBatch['batch_name'] = currentBatchName
            newBatch['compound_id'] = currentCompId
            newBatch['test_plan_id'] = currentTestPlanId
            newBatch['samples'] = [cleaned_data]
            self.batches.append(newBatch)
        return self.batches


if __name__=='__main__':
    dm = DataManager()