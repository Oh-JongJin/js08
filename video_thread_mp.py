#!/usr/bin/env python3
#
# Copyright 2021-2022 Sijung Co., Ltd.
#
# Authors:
#     cotjdals5450@gmail.com (Seong Min Chae)
#     5jx2oh@gmail.com (Jongjin Oh)

import os
import cv2
import time
import numpy as np

from model import JS08Settings
from target_info import TargetInfo
from save_log import log

# seongmin
from model_print import Tf_model


def producer(queue):
    front_cap_name = JS08Settings.get('front_camera_name')
    rear_cap_name = JS08Settings.get('rear_camera_name')

    front_cap = cv2.VideoCapture(JS08Settings.get('front_camera_rtsp'))
    rear_cap = cv2.VideoCapture(JS08Settings.get('rear_camera_rtsp'))

    # NE, EN, ES, SE, SW, WS, WN, NW = [], [], [], [], [], [], [], []

    if rear_cap.isOpened() and front_cap.isOpened():
        # print('Video thread start.')
        log(JS08Settings.get('current_id'), 'Video thread start')
        target_info = TargetInfo()
        # 성민추가
        tf_model = Tf_model()

        while True:
            epoch = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            date = epoch[2:8]
            

            if rear_cap.isOpened() is False or front_cap.isOpened() is False:
                break

            if epoch[-2:] == '00':
                print(epoch)
                front_target_name, front_left_range, front_right_range, front_distance, front_azimuth = \
                    target_info.get_target(front_cap_name)
                rear_target_name, rear_left_range, rear_right_range, rear_distance, rear_azimuth = \
                    target_info.get_target(rear_cap_name)

                front_target_name_NE, front_left_range_NE, front_right_range_NE, front_distance_NE, front_azimuth_NE = \
                    target_info.get_target_from_azimuth(front_cap_name, 'NE')

                front_target_name_EN, front_left_range_EN, front_right_range_EN, front_distance_EN, front_azimuth_EN = \
                    target_info.get_target_from_azimuth(front_cap_name, 'EN')

                front_target_name_ES, front_left_range_ES, front_right_range_ES, front_distance_ES, front_azimuth_ES = \
                    target_info.get_target_from_azimuth(front_cap_name, 'ES')

                front_target_name_SE, front_left_range_SE, front_right_range_SE, front_distance_SE, front_azimuth_SE = \
                    target_info.get_target_from_azimuth(front_cap_name, 'SE')

                rear_target_name_SW, rear_left_range_SW, rear_right_range_SW, rear_distance_SW, rear_azimuth_SW = \
                    target_info.get_target_from_azimuth(rear_cap_name, 'SW')

                rear_target_name_WS, rear_left_range_WS, rear_right_range_WS, rear_distance_WS, rear_azimuth_WS = \
                    target_info.get_target_from_azimuth(rear_cap_name, 'WS')

                rear_target_name_WN, rear_left_range_WN, rear_right_range_WN, rear_distance_WN, rear_azimuth_WN = \
                    target_info.get_target_from_azimuth(rear_cap_name, 'WN')

                rear_target_name_NW, rear_left_range_NW, rear_right_range_NW, rear_distance_NW, rear_azimuth_NW = \
                    target_info.get_target_from_azimuth(rear_cap_name, 'NW')

                if len(front_left_range_NE) < 4 and len(front_left_range_EN) < 4 and len(front_left_range_ES) < 4 \
                        and len(front_left_range_ES) < 4 and len(rear_left_range_SW) < 4 and len(rear_left_range_WS) < 4 \
                        and len(rear_left_range_WN) < 4 and len(rear_left_range_NW) < 4:
                    continue
                else:
                    pass

                image_save_path = JS08Settings.get('image_save_path')
                os.makedirs(f'{image_save_path}/vista/{front_cap_name}/{date}', exist_ok=True)
                os.makedirs(f'{image_save_path}/vista/{rear_cap_name}/{date}', exist_ok=True)
                os.makedirs(f'{image_save_path}/thumbnail/{front_cap_name}/{date}', exist_ok=True)
                os.makedirs(f'{image_save_path}/thumbnail/{rear_cap_name}/{date}', exist_ok=True)

                front_ret, front_frame = front_cap.read()
                rear_ret, rear_frame = rear_cap.read()
                # front_cap.release()
                # rear_cap.release()
                if rear_cap.isOpened() is False or front_cap.isOpened() is False:
                    front_cap = cv2.VideoCapture(JS08Settings.get('front_camera_rtsp'))
                    rear_cap = cv2.VideoCapture(JS08Settings.get('rear_camera_rtsp'))

                front_ret, front_frame = front_cap.read()
                rear_ret, rear_frame = rear_cap.read()

                if not front_ret or not rear_ret:
                    print(f'Found Error; Rebuilding stream in {time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(time.time()))}')

                # try:
                #     # visibility_front = target_info.minprint(epoch[:-2], front_left_range, front_right_range,
                #     #                                         front_distance, front_frame, front_cap_name)
                #     # visibility_rear = target_info.minprint(epoch[:-2], rear_left_range, rear_right_range,
                #     #                                        rear_distance, rear_frame, rear_cap_name)
                #     # 성민추가
                #     visibility_front = tf_model.inference(epoch[:-2], front_left_range, front_right_range,
                #                                             front_distance, front_frame, front_cap_name, "front")
                #     visibility_rear = tf_model.inference(epoch[:-2], rear_left_range, rear_right_range,
                #                                            rear_distance, rear_frame, rear_cap_name, "rear")
                # except AttributeError:
                #     print("AttributeError")
                #     continue
                print("start_inference")
                # visibility_front_NE = target_info.minprint(epoch[:-2], front_left_range_NE, front_right_range_NE,
                #                                            front_distance_NE, front_frame, front_cap_name)
                # visibility_front_EN = target_info.minprint(epoch[:-2], front_left_range_EN, front_right_range_EN,
                #                                            front_distance_EN, front_frame, front_cap_name)
                # visibility_front_ES = target_info.minprint(epoch[:-2], front_left_range_ES, front_right_range_ES,
                #                                            front_distance_ES, front_frame, front_cap_name)
                # visibility_front_SE = target_info.minprint(epoch[:-2], front_left_range_SE, front_right_range_SE,
                #                                            front_distance_SE, front_frame, front_cap_name)

                # visibility_rear_SW = target_info.minprint(epoch[:-2], rear_left_range_SW, rear_right_range_SW,
                #                                           rear_distance_SW, rear_frame, rear_cap_name)
                # visibility_rear_WS = target_info.minprint(epoch[:-2], rear_left_range_WS, rear_right_range_WS,
                #                                           rear_distance_WS, rear_frame, rear_cap_name)
                # visibility_rear_WN = target_info.minprint(epoch[:-2], rear_left_range_WN, rear_right_range_WN,
                #                                           rear_distance_WN, rear_frame, rear_cap_name)
                # visibility_rear_NW = target_info.minprint(epoch[:-2], rear_left_range_NW, rear_right_range_NW,
                #                                           rear_distance_NW, rear_frame, rear_cap_name)
                # 성민추가
                visibility_front_NE = tf_model.inference(epoch[:-2], front_left_range_NE, front_right_range_NE,
                                                           front_distance_NE, front_frame, front_cap_name, "NE")
                visibility_front_EN = tf_model.inference(epoch[:-2], front_left_range_EN, front_right_range_EN,
                                                           front_distance_EN, front_frame, front_cap_name, "EN")
                visibility_front_ES = tf_model.inference(epoch[:-2], front_left_range_ES, front_right_range_ES,
                                                           front_distance_ES, front_frame, front_cap_name, "ES")
                visibility_front_SE = tf_model.inference(epoch[:-2], front_left_range_SE, front_right_range_SE,
                                                           front_distance_SE, front_frame, front_cap_name, "SE")

                visibility_rear_SW = tf_model.inference(epoch[:-2], rear_left_range_SW, rear_right_range_SW,
                                                          rear_distance_SW, rear_frame, rear_cap_name, "SW")
                visibility_rear_WS = tf_model.inference(epoch[:-2], rear_left_range_WS, rear_right_range_WS,
                                                          rear_distance_WS, rear_frame, rear_cap_name, "WS")
                visibility_rear_WN = tf_model.inference(epoch[:-2], rear_left_range_WN, rear_right_range_WN,
                                                          rear_distance_WN, rear_frame, rear_cap_name, "WN")
                visibility_rear_NW = tf_model.inference(epoch[:-2], rear_left_range_NW, rear_right_range_NW,
                                                          rear_distance_NW, rear_frame, rear_cap_name, "NW")
                # if len(NE) >= 20:
                #     del NE[0]
                #     del EN[0]
                #     del ES[0]
                #     del SE[0]
                #     del SW[0]
                #     del WS[0]
                #     del WN[0]
                #     del NW[0]

                # NE.append(float(visibility_front_NE))
                # EN.append(float(visibility_front_EN))
                # ES.append(float(visibility_front_ES))
                # SE.append(float(visibility_front_SE))
                # SW.append(float(visibility_rear_SW))
                # WS.append(float(visibility_rear_WS))
                # WN.append(float(visibility_rear_WN))
                # NW.append(float(visibility_rear_NW))

                # NE_average = round(float(np.mean(NE)))
                # EN_average = round(float(np.mean(EN)))
                # ES_average = round(float(np.mean(ES)))
                # SE_average = round(float(np.mean(SE)))
                # SW_average = round(float(np.mean(SW)))
                # WS_average = round(float(np.mean(WS)))
                # WN_average = round(float(np.mean(WN)))
                # NW_average = round(float(np.mean(NW)))

                # visibility = {'NE': round(float(NE_average), 3), 'EN': round(float(EN_average), 3),
                #               'ES': round(float(ES_average), 3), 'SE': round(float(SE_average), 3),
                #               'SW': round(float(SW_average), 3), 'WS': round(float(WS_average), 3),
                #               'WN': round(float(WN_average), 3), 'NW': round(float(NW_average), 3)}
                # Delete Running average
                visibility = {'NE': round(float(visibility_front_NE), 3), 'EN': round(float(visibility_front_EN), 3),
                              'ES': round(float(visibility_front_ES), 3), 'SE': round(float(visibility_front_SE), 3),
                              'SW': round(float(visibility_rear_SW), 3), 'WS': round(float(visibility_rear_WS), 3),
                              'WN': round(float(visibility_rear_WN), 3), 'NW': round(float(visibility_rear_NW), 3)}
                print("Model End")
                queue.put(visibility)

                if JS08Settings.get('image_size') == 0:  # Original size
                    cv2.imwrite(f'{image_save_path}/vista/{front_cap_name}/{date}/{epoch}.png', front_frame)
                    cv2.imwrite(f'{image_save_path}/vista/{rear_cap_name}/{date}/{epoch}.png', rear_frame)

                elif JS08Settings.get('image_size') == 1:  # Original size
                    front_frame = cv2.resize(front_frame, (1920, 640), interpolation=cv2.INTER_AREA)
                    rear_frame = cv2.resize(rear_frame, (1920, 640), interpolation=cv2.INTER_AREA)

                    cv2.imwrite(
                        f'{image_save_path}/vista/{front_cap_name}/{date}/{epoch}.png', front_frame)
                    cv2.imwrite(
                        f'{image_save_path}/vista/{rear_cap_name}/{date}/{epoch}.png', rear_frame)

                elif JS08Settings.get('image_size') == 2:  # FHD size
                    front_frame = cv2.resize(front_frame, (1920, 640), interpolation=cv2.INTER_AREA)
                    rear_frame = cv2.resize(rear_frame, (1920, 640), interpolation=cv2.INTER_AREA)

                    cv2.imwrite(
                        f'{image_save_path}/vista/{front_cap_name}/{date}/{epoch}.png', front_frame)
                    cv2.imwrite(
                        f'{image_save_path}/vista/{rear_cap_name}/{date}/{epoch}.png', rear_frame)

                # Save thumbnail image
                # epoch = time.strftime('%Y-%m-%d %H:%M:00', time.localtime(time.time()))
                front_frame = cv2.resize(front_frame, (314, 105), interpolation=cv2.INTER_AREA)  # Thumbnail size
                rear_frame = cv2.resize(rear_frame, (314, 105), interpolation=cv2.INTER_AREA)
                cv2.imwrite(
                    f'{image_save_path}/thumbnail/{front_cap_name}/{date}/{epoch}.jpg', front_frame)
                cv2.imwrite(
                    f'{image_save_path}/thumbnail/{rear_cap_name}/{date}/{epoch}.jpg', rear_frame)

                time.sleep(1)
                front_cap.release()
                rear_cap.release()
                front_cap = cv2.VideoCapture(JS08Settings.get('front_camera_rtsp'))
                rear_cap = cv2.VideoCapture(JS08Settings.get('rear_camera_rtsp'))

            cv2.destroyAllWindows()
    else:
        print('cap closed')
