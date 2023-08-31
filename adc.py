import time
import drivers.ADS1263
import RPi.GPIO as GPIO


def read_adc(test_adc1=True,
             test_adc2=False,
             test_adc1_rate=False,
             test_rtd=False,
             ref_voltage=5.08):
    readings = dict()

    try:
        adc = ADS1263.ADS1263()

        # The faster the rate, the worse the stability
        # and the need to choose a suitable digital filter(REG_MODE1)
        if adc.ADS1263_init_ADC1('ADS1263_400SPS') == -1:
            readings['error'] = 'ADS1263_400SPS initialization failed'
            return

        adc.ADS1263_SetMode(0)  # 0 is singleChannel, 1 is diffChannel

        # todo: not sure what these do?
        # ADC.ADS1263_DAC_Test(1, 1)      # Open IN6
        # ADC.ADS1263_DAC_Test(0, 1)      # Open IN7

        if test_adc1:  # ADC1 Test
            channel_list = [0, 1, 2, 3, 4]  # The channel must be less than 10
            while True:
                adc_value = adc.ADS1263_GetAll(channel_list)  # get ADC1 value
                for i in channel_list:
                    if adc_value[i] >> 31 == 1:
                        readings[i] = "ADC1 IN%d = -%lf" % (i, (ref_voltage * 2 - adc_value[i] * ref_voltage / 0x80000000))
                    else:
                        readings[i] = "ADC1 IN%d = %lf" % (i, (adc_value[i] * ref_voltage / 0x7fffffff))  # 32bit

        elif test_adc2:
            if adc.ADS1263_init_ADC2('ADS1263_ADC2_400SPS') == -1:
                readings['error'] = 'ADS1263_ADC2_400SPS initialization failed'
                return

            while True:
                adc_value = adc.ADS1263_GetAll_ADC2()  # get ADC2 value
                for i in range(0, 10):
                    if adc_value[i] >> 23 == 1:
                        readings[i] = "ADC2 IN%d = -%lf" % (i, (ref_voltage * 2 - adc_value[i] * ref_voltage / 0x800000))
                    else:
                        readings[i] = "ADC2 IN%d = %lf" % (i, (adc_value[i] * ref_voltage / 0x7fffff))  # 24bit

        elif test_adc1_rate:  # rate test
            time_start = time.time()
            adc_value = []
            is_single_channel = True
            if is_single_channel:
                while True:
                    adc_value.append(adc.ADS1263_GetChannalValue(0))
                    if len(adc_value) == 5000:
                        time_end = time.time()
                        print(time_start, time_end)
                        print(time_end - time_start)
                        readings['frequency'] = 5000 / (time_end - time_start)
                        break
            else:
                while True:
                    adc_value.append(adc.ADS1263_GetChannalValue(0))
                    if len(adc_value) == 5000:
                        time_end = time.time()
                        print(time_start, time_end)
                        print(time_end - time_start)
                        readings['frequency'] = 5000 / (time_end - time_start)
                        break

        elif test_rtd:  # RTD Test
            while True:
                adc_value = adc.ADS1263_RTD_Test()
                RES = adc_value / 2147483647.0 * 2.0 * 2000.0  # 2000.0 -- 2000R, 2.0 -- 2*i
                readings['res'] = ("%lf" % RES)
                TEMP = (RES / 100.0 - 1.0) / 0.00385  # 0.00385 -- pt100
                readings['temp'] = ("%lf" % TEMP)

        adc.ADS1263_Exit()

    except IOError as e:
        print(e)
        readings['error'] = e.message

    except KeyboardInterrupt:
        print("ctrl + c:")
        print("Program end")
        adc.ADS1263_Exit()
        exit()

    return readings
