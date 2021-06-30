import os
from PIL import Image
from configparser import ConfigParser


def get_percent_adjust(page_number, size_goal, data):

    is_even = (page_number//2) == (page_number/2)
    if is_even:
        key_ = 'even'
    else:
        key_ = 'odd'

    list_page = data['list_page'][key_]
    list_height = data['list_height'][key_]
    change_size_percent = data['change_size_percent'][key_]

    size_estimated = \
        list_height[0] + change_size_percent * (page_number - list_page[0])

    percent_adjust = size_goal / size_estimated

    # log
    after_adjust = size_estimated * percent_adjust
    print(f'Page {page_number}')
    print(f'content_size:     {size_estimated}')
    print(f'percent_adjust:   {percent_adjust}')
    print(f'content_adjusted: {after_adjust}')
    print('')

    return percent_adjust


def get_change_size_percent_per_page(list_page, list_size):

    qt_page = list_page[1] - list_page[0]
    size_diff = list_size[1] - list_size[0]
    change_size_percent = size_diff/qt_page
    return change_size_percent


def get_data_model(list_odd_page, list_odd_height,
                   list_even_page, list_even_height):

    data = {}
    change_size_percent = {}
    list_page = {}
    list_height = {}

    change_size_percent['odd'] = \
        get_change_size_percent_per_page(list_page=list_odd_page,
                                         list_size=list_odd_height)
    change_size_percent['even'] = \
        get_change_size_percent_per_page(list_page=list_even_page,
                                         list_size=list_even_height)

    list_page['even'] = list_even_page
    list_page['odd'] = list_odd_page

    list_height['even'] = list_even_height
    list_height['odd'] = list_odd_height

    data['change_size_percent'] = change_size_percent
    data['list_page'] = list_page
    data['list_height'] = list_height
    return data


def get_resize_resolution(actual_height, actual_width, percent_adjust):

    height = actual_height * percent_adjust
    width = actual_width * percent_adjust
    tuple_resize_resolution = (int(height), int(width))
    return tuple_resize_resolution


def get_actual_resolution(path_file):

    image = Image.open(path_file)
    height, width,  = image.size
    return height, width


def process_resize(path_file, tuple_resize_resolution, file_path_dest):

    colorImage = Image.open(path_file)
    edited_image = colorImage.resize(tuple_resize_resolution)
    edited_image.save(file_path_dest)


def resize_equalize(path_dir, folder_path_dest,
                    list_odd_page, list_odd_height,
                    list_even_page, list_even_height):

    ## define content size goal
    size_goal = max(list_odd_height + list_even_height)

    data = get_data_model(list_odd_page, list_odd_height,
                          list_even_page, list_even_height)

    list_path_file = []
    for root, _, files in os.walk(path_dir):
        for file in files:
            path_file = os.path.join(root, file)
            list_path_file.append(path_file)

    # get sample height and width
    sample_path_file = list_path_file[0]
    actual_height, actual_width = get_actual_resolution(sample_path_file)
    print(f'Images height: {actual_height}')
    print(f'Images width: {actual_width}\n')

    for path_file in list_path_file:
        file_name = os.path.basename(path_file)
        file_name_without_extension = os.path.splitext(file_name)[0]
        extension = os.path.splitext(file_name)[1]
        file_name_dest = file_name_without_extension + '-resize' + extension

        # get main variables
        ## input
        file_path_dest = os.path.join(folder_path_dest,
                                      file_name_dest)
        file_name_number = int(file_name_without_extension)

        ## output variables
        percent_adjust = \
            get_percent_adjust(file_name_number, size_goal, data)
        tuple_resize_resolution = \
            get_resize_resolution(actual_height, actual_width, percent_adjust)

        # process resize
        process_resize(path_file, tuple_resize_resolution, file_path_dest)


def main():

    config = ConfigParser()
    config.read('config.ini')
    default_config = dict(config['default'])

    folder_path_input = default_config['folder_path_input']
    folder_path_output = default_config['folder_path_output']

    # variables: pagination and content height
    first_odd_page = int(default_config['first_odd_page'])
    last_odd_page = int(default_config['last_odd_page'])

    first_odd_height = int(default_config['first_odd_height'])
    last_odd_height = int(default_config['last_odd_height'])

    first_even_page = int(default_config['first_even_page'])
    last_even_page = int(default_config['last_even_page'])

    first_even_height = int(default_config['first_even_height'])
    last_even_height = int(default_config['last_even_height'])

    # main variables
    list_odd_page = [first_odd_page, last_odd_page]
    list_odd_height = [first_odd_height, last_odd_height]
    list_even_page = [first_even_page, last_even_page]
    list_even_height = [first_even_height, last_even_height]

    print('\n==Images Size Equalizer==\n')
    print(f'folder_path_input: {folder_path_input}')
    print(f'folder_path_output: {folder_path_output}')
    print(f'list_odd_page: {list_odd_page}')
    print(f'list_odd_height: {list_odd_height}')
    print(f'list_even_page: {list_even_page}')
    print(f'list_even_height: {list_even_height}\n')

    # process resize equalize in all pages
    resize_equalize(folder_path_input, folder_path_output,
                    list_odd_page, list_odd_height,
                    list_even_page, list_even_height)


if __name__ == "__main__":
    main()