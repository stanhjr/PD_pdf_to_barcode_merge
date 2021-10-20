import fitz
import json
import psycopg2
import time
from config import host, user, db_name, password
from barcode import ITF
from barcode.writer import ImageWriter


def glue_the_barcode():
    """
    generating barcode and glue barcode in all pages of pdf file
    exception add new element in json file missing lines.txt
    """
    try:
        while True:
            next_row = cursor.fetchone()
            if next_row:
                id, barcode_number, file_path = next_row
                print(next_row)
                with open('barcode.jpeg', 'wb') as f:
                    ITF(barcode_number, writer=ImageWriter()).write(f)

                time.sleep(1)
                with open('barcode_last.txt', 'w') as f:
                    f.write(str(id))

                time.sleep(1)
                input_file = file_path
                barcode_file = "barcode.jpeg"

                file_handle = fitz.Document(input_file)
                for page in file_handle:
                    page.insert_image(image_rectangle, filename=barcode_file)
                    file_handle.saveIncr()
            else:
                break
    except RuntimeError:
        with open('missing lines.txt', 'r') as f:
            json_string = f.read()
            missing_lines = json.loads(json_string)
        with open('missing lines.txt', 'w') as f:
            missing_lines.append(id)
            missing_set = set(missing_lines)
            missing_lines = list(missing_set)
            missing_lines = json.dumps(missing_lines)
            f.write(missing_lines)


# def lost_lines_handling():
#     """
#     rereads lost lines, tries to fix them
#     """
#     with open('missing lines.txt', 'r') as f:
#         json_string = f.read()
#         missing_lines = json.loads(json_string)
#     if missing_lines:
#         for elem in missing_lines:
#             print('Пытаюсь исправить ошибку')
#             line_id = int(elem)
#             with connection.cursor() as curs:
#                 curs.execute(
#                     "SELECT * FROM test_pdf WHERE id = (%s)", (line_id,)
#                 )
#                 glue_the_barcode()
#                 missing_lines.delete(line_id)
#                 with open('missing lines.txt', 'w') as f:
#                     missing_lines = json.dumps(missing_lines)
#                     f.write(missing_lines)


image_rectangle = fitz.Rect(0, 0, 100, 75)

k = 0
while True:
    k += 1
    print(f'Моё {k} подключение')
    time.sleep(10)

    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    # lost_lines_handling()

    with open('barcode_last.txt', 'r') as f:
        id_pk = int(f.read())
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM test_pdf WHERE id > (%s)", (id_pk,)
        )
        glue_the_barcode()

    connection.commit()
