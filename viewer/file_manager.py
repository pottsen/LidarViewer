from las_data import Las_Data


class File_Manager:

    def __init__(self):
        self.file_dict = {}
        self.manager_dict = {'Crop': None, 'Align': None, 'Depth':None}

    def add_manager(self, key, manager):
        self.manager_dict[key] = manager

    def add_file(self, file_path):
        las_data = Las_Data(file_path)
        self.file_dict[file_path] = las_data
        print(file_path, ' added to manager')
        self.push_file_to_child_managers(file_path)

    def push_file_to_child_managers(self, file_path):
        print('Adding file to other managers')
        for key in self.manager_dict:
            self.manager_dict[key].add_file_object(file_path)

    def remove_file(self, file_path):
        self.file_dict.pop(file_path, None)
        print(file_path,' removed from manager')
        self.remove_file_from_child_managers(file_path)

    def remove_file_from_child_managers(self, file_path):
        print('Removing file from other managers')
        for key in self.manager_dict:
            self.manager_dict[key].remove_file_object(file_path)

    def remove_cropped_points(self, selected, file_path):
        self.file_dict[file_path].remove_cropped_points(selected)

    def update_aligned_points(self, points, file_path):
        self.file_dict[file_path].update_aligned_points(points)


