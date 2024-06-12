import os

DATA_FOLDER = 'data'

def menu(): 
    print('1. Canvas Pull')
    print('2. GitHub Classroom Sync')
    print('3. Canvas Push')
    print('4. Exit')

def canvas_file_select() -> str: 
    canvas_files = os.listdir(DATA_FOLDER)
    print('Select file to pull from the list below:')
    canvas_files.sort(key=lambda x: os.path.getctime(os.path.join(DATA_FOLDER, x)), reverse=True)
    for seq, name in enumerate(canvas_files): 
        print(f'{seq+1}. {name}')
    select = int(input('? '))
    return canvas_files[select-1]

if __name__ == "__main__":
    option = -1
    while option != 4: 
        menu()
        option = int(input('? '))
        if option == 1:
            print('Canvas Pull')
            print(canvas_file_select())
        elif option == 2: 
            print('GitHub Classroom Sync')
        elif option == 3: 
            print('Canvas Push')
        