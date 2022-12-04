import os
import json
import sqlite3

settings_file_path = os.path.join(os.path.split(__file__)[0], 'settings.json')
database_folder_path = os.path.join(os.path.split(__file__)[0], '.database')

def load_settings_file() -> dict:
    if not os.path.exists(settings_file_path):
        settings_dict = {"monitor_folders":[]}
        with open(mode="w", file=settings_file_path) as f:
            json.dump(settings_dict, f)
        return settings_dict
    with open(mode="r", file=settings_file_path) as f:
        return json.load(f)

def init_database(db_name):
    if not os.path.exists(database_folder_path):
        os.mkdir(database_folder_path)

    conn = sqlite3.connect(os.path.join(database_folder_path, db_name + ".db"))
    cur = conn.cursor()

    sql = '''
        create table if not exists files_info (
            id integer primary key autoincrement,
            path text,
            timestamp text
        )
    '''

    cur.execute(sql)
    conn.commit()

    return (conn, cur)

def get_files_info(folder_path):
    files_info = []
    for curDir, _,  files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(curDir, file)
            files_info.append((
                file_path,
                str(os.stat(file_path).st_mtime).split('.')[0],
            ))
    return files_info

def comparison_files_info(current_files_info, cur, conn):
    current_paths = [path[0] for path in current_files_info]

    cur.execute("select path, timestamp from files_info")

    pervious_files_info = cur.fetchall()
    pervious_paths = [path[0] for path in pervious_files_info]
    pervious_timestamps = [timestamp[1] for timestamp in pervious_files_info]

    pervious_files_info = set(pervious_files_info)

    intersection_files_info = pervious_files_info & set(current_files_info)

    updated_files_info = list(set(current_files_info) - intersection_files_info) + list(pervious_files_info - intersection_files_info)

    added_files_info = []
    deleted_paths = []
    changed_files_info = []

    pervious_files_info = list(pervious_files_info)

    for file_info in updated_files_info:
        if file_info[0] not in pervious_paths:
            added_files_info.append(file_info)
            continue
        if file_info[0] not in current_paths:
            deleted_paths.append(file_info[0])
            continue
        pervious_index = pervious_paths.index(file_info[0])
        if file_info[1] != pervious_timestamps[pervious_index]:
            changed_files_info.append(pervious_files_info[pervious_index])
    
    updated_database(added_files_info, deleted_paths, cur, conn)
    
    return (added_files_info, deleted_paths, changed_files_info)

def updated_database(added_files_info, deleted_paths, cur, conn):
    cur.executemany('insert into files_info (path, timestamp) values (?, ?)', added_files_info)
    for path in deleted_paths:
        cur.execute('delete from files_info where path="%s"' % path)
    conn.commit()

def main():
    for folder_path in load_settings_file()['monitor_folders']:
        # _, folder_name = os.path.split(folder_path)
        conn, cur = init_database(folder_path.replace('\\', "-").replace('/', "-").replace(':', '-'))
        current_files_info = get_files_info(folder_path)
        # added_files_info, deleted_paths, updated_files_info = comparison_files_info(current_files_info, cur, conn)


if __name__ == "__main__":
    main()