from nptdms import TdmsFile, TdmsWriter, RootObject, GroupObject, ChannelObject
import os
import numpy as np

class TdmsOperation(object):
    def __init__(self):
        self.tdmsobj = None
    
    def open(self, filepath):
        self.tdmsobj = TdmsFile.read(filepath)
        return self.tdmsobj
    
    def get_all_groups(self):
        groups = [g.name for g in self.tdmsobj.groups()]
        return groups
    
    def get_property_by_group_name(self, groupName):
        group = self.tdmsobj[groupName]
        properties = {}
        for k,v in group.properties.items():
            properties[k]=v
        return properties
    
    def get_all_channels_by_group_name(self, groupName):
        group = self.tdmsobj[groupName]
        channels = group.channels()
        return channels

    def how_many_channels_in_group_name(self, groupName):
        return len(self.get_all_channels_by_group_name(groupName))

    def get_channel_by_group_and_channel(self, groupName, channelName):
        group = self.tdmsobj[groupName]
        channel = group[channelName]
        return channel

    def get_property_by_group_and_channel(self, groupName, channelName):
        group = self.tdmsobj[groupName]
        channel = group[channelName]
        properties = {}
        for k,v in channel.properties.items():
            properties[k]=v
        return properties

    def get_all_data_in_group(self, groupName):
        group = self.tdmsobj[groupName]
        all_data = []
        for channel in group.channels():
            data = channel[:]
            all_data.append(data)
        return all_data

    def get_single_data_in_channel(self, groupName, channelName):
        channel = self.get_channel_by_group_and_channel(groupName,channelName)
        data = channel[:]
        return data

    def write_array_data(self, filepath, groupName, rawData, tags={}, sampleInfo={"batchId": None, "batchName": '',"sampleId": None}):
        nextIndexOfChannel = 0
        hasGroup = False
        root_object = RootObject(properties=sampleInfo)
        group_object = GroupObject(groupName, properties={'data_form': 'array'})
        channel_object = ChannelObject(groupName, 'm0', rawData, properties=tags)
        if os.path.exists(filepath):
            tdms_file = TdmsFile.read(filepath)
            original_groups = tdms_file.groups()
            original_channels = [chan for group in original_groups for chan in group.channels()]

            try:
                hasGroup = tdms_file[groupName] is not None
            except KeyError:
                hasGroup = False
            print(f'has group? {hasGroup}')
            if hasGroup:
                channels = tdms_file[groupName].channels()
                print(channels)
                nextIndexOfChannel = len(channels)
            channelName = f'm{nextIndexOfChannel}'
            channel_object = ChannelObject(groupName, channelName, rawData, properties=tags)
            with TdmsWriter(filepath,mode='a') as tdms_writer:
                # root_object = RootObject(tdms_file.properties)
                # channels_to_copy = [chan for chan in original_channels]
                # channels_to_copy.append(channel_object)
                # tdms_writer.write_segment([root_object] + original_groups + channels_to_copy)
                # Write first segment
                tdms_writer.write_segment([
                    root_object,
                    group_object,
                    channel_object])
        else:
            with TdmsWriter(filepath) as tdms_writer:
                # Write first segment
                tdms_writer.write_segment([
                    root_object,
                    group_object,
                    channel_object])

    def write_waveform_data(self, filepath, groupName, time_data=[], y_data=[], tags={}, sampleInfo={"batchId": None, "batchName": '',"sampleId": None}):
        nextIndexOfChannel = 0
        if os.path.exists(filepath):
            self.open(filepath)
            nextIndexOfChannel = self.how_many_channels_in_group_name(groupName) + 1
            self.close()
            
        time_channelName = f'm{nextIndexOfChannel}_t'
        value_channelName = f'm{nextIndexOfChannel}_y'
        root_object = RootObject(properties=sampleInfo)
        group_object = GroupObject(groupName, properties={'data_form': 'waveform'})
        with TdmsWriter(filepath) as tdms_writer:
            # Write time data segment
            time_channel_object = ChannelObject(groupName, time_channelName, time_data, properties={})
            tdms_writer.write_segment([
                root_object,
                group_object,
                time_channel_object])     
            # Write value data segment
            value_channel_object = ChannelObject(groupName, value_channelName, y_data, properties=tags)
            tdms_writer.write_segment([
                root_object,
                group_object,
                value_channel_object])          
    
    def copy_tdms(self, filePath, targetPath):
        original_file = TdmsFile(filePath)
        original_groups = original_file.groups()
        original_channels = [chan for group in original_groups for chan in group.channels()]

        with TdmsWriter(targetPath) as copied_file:
            root_object = RootObject(original_file.properties)
            channels_to_copy = [chan for chan in original_channels]
            copied_file.write_segment([root_object] + original_groups + channels_to_copy)

    def close(self):
        self.tdmsobj.close()


if __name__=='__main__':
    td = TdmsOperation()
    currFolder = os.path.dirname(__file__)
    filePath = os.path.join(currFolder,'test','mytdms.tdms')
    
    # td.open(filePath)
    # groups = td.get_all_groups()
    # # with TdmsFile.open(filePath) as tdms_file:
    # #     # Use tdms_file
    # #     groups = tdms_file.groups()
    # #     print(groups)
    # #     [print(g.channels()) for g in groups]
    # print('')
    # print('### print properties in group ###')
    # for g in groups:
    #     print(g)
    #     print(td.get_property_by_group_name(g))
    #     print('')

    # print('### print properties in channel ###')
    # for g in groups:
    #     print(g)
    #     for c in td.get_all_channels_by_group_name(g):
    #         print(c)
    #         print(td.get_property_by_group_and_channel(g,c))
    #         print('')
    #     print('')

    # print('### print data in channel ###')
    # for g in groups:
    #     print(g)
    #     for c in td.get_all_channels_by_group_name(g):
    #         print(c)
    #         print(td.get_single_data_in_channel(g,c))
    #         print('')
    #     print('')

    # td.close()

    # td = TdmsOperation()
    # targetPath = os.path.join(currFolder,'test','copy_mytdms.tdms')
    # td.copy_tdms(filePath, targetPath)

    rawData = np.random.randint(100, size=10)
    td.write_array_data(filePath,'Density', rawData, sampleInfo={"batchId": 1, "batchName": 'my batch',"sampleId": 1})