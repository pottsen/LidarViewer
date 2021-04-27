from las_data import Las_Data


class File_Manager:

    def __init__(self):
        self.file_dict = {}
        self.manager_dict = {'Crop': None, 'Align': None, 'Depth':None}

    def add_manager(self, key, manager):
        # add crop, alignment, depth manager links
        self.manager_dict[key] = manager

    def add_file(self, file_path):
        # add loaded file data to master manager
        las_data = Las_Data(file_path)
        self.file_dict[file_path] = las_data
        print(file_path, ' added to manager')
        self.push_file_to_child_managers(file_path)

    def push_file_to_child_managers(self, file_path):
        # push loaded file to other managers
        print('Adding file to other managers')
        for key in self.manager_dict:
            self.manager_dict[key].add_file_object(file_path)

    def remove_file(self, file_path):
        # remove file
        self.file_dict.pop(file_path, None)
        print(file_path,' removed from manager')
        self.remove_file_from_child_managers(file_path)

    def remove_file_from_child_managers(self, file_path):
        # remove file from all managers
        print('Removing file from other managers')
        for key in self.manager_dict:
            self.manager_dict[key].remove_file_object(file_path)

    def remove_cropped_points(self, selected, file_path):
        # modify file points for cropping
        self.file_dict[file_path].remove_cropped_points(selected)

    def update_aligned_points(self, points, file_path):
        # modify file points based on alignment
        self.file_dict[file_path].update_aligned_points(points)

    def reset_files(self):
        for key in self.file_dict.keys():
            self.file_dict[key] = Las_Data(key)
            print(key, ' reset in manager')



