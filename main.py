#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import Tkinter
from line import *
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import WebDriverException

def get_bill(username, password):
    while True:
        browser = None
        try:
            browser = webdriver.Chrome()
            browser.get('http://www.att.com')
            username_box = browser.find_element_by_id('userid')
            username_box.send_keys(username)
            password_box = browser.find_element_by_id('userPassword')
            password_box.send_keys(password)
            password_box.submit()
            while True:
                try:
                    bill_details_button = WebDriverWait(browser, 80).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="ge5p_z2_s3002"]')))
                    bill_details_button.click()
                    break
                except WebDriverException:
                    no_button = browser.find_element_by_xpath('//*[@id="top"]/div[11]/div/div/div/div/div/div[2]/div[2]/a')
                    no_button.click()
            bill = WebDriverWait(browser, 40).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="toggleGroup10"]/div[2]'))).get_attribute('outerHTML')
            browser.quit()
            return bill
        except:
            print('Something went wrong! Starting over!')
            browser.quit()

def get_difference(charges):
    mainline = charges[len(charges) - 1]
    charges.sort()
    if (len(charges) != len(set(charges))):
        for i in range(0, len(charges) - 1):
            if charges[i] == charges[i + 1]:
                return mainline - charges[i]
    else:
        return mainline - charges[2]

def get_period(period):
    start = datetime.strptime(period[: period.find('-') - 1], '%b %d')
    end = datetime.strptime(period[period.find('-') + 2 :], '%b %d, %Y')
    if start.month == 12:
        start = start.replace(year = end.year - 1)
    else:
        start = start.replace(year = end.year)
    return start.strftime('%x') + ' - ' + end.strftime('%x')

def get_total(lines):
    return sum([line.get_total() for line in lines])

def GUI(lines, period):
    window = Tkinter.Tk()
    window.wm_title('Current Bill for %s' % period)
    text_period = Tkinter.Text(window, height = 2, width = len(get_period(period)), bd = 5)
    text_period.insert(Tkinter.INSERT, '%s' % get_period(period))
    text_period.pack(anchor = Tkinter.NE) 
    frame_table = Tkinter.Frame(window)
    frame_table.pack() 
    frame_total = Tkinter.Frame(window) 
    text_line_total = Tkinter.Text(frame_table, height = 8, width = 10, bd = 5)
    text_line_total.insert(Tkinter.INSERT, '    Total\n\n') 
    text_government_fees = Tkinter.Text(frame_table, height = 8, width = 15, bd = 5)
    text_government_fees.insert(Tkinter.INSERT, ' Government \nFees & Taxes\n')  
    text_surcharges = Tkinter.Text(frame_table, height = 8, width = 15, bd = 5)
    text_surcharges.insert(Tkinter.INSERT, 'Surcharges\n and Fees\n')   
    text_usage_charges = Tkinter.Text(frame_table, height = 8, width = 15, bd = 5)
    text_usage_charges.insert(Tkinter.INSERT, 'Talk Usage\n  Charges\n')  
    text_monthly_charges = Tkinter.Text(frame_table, height = 8, width = 15, bd = 5)
    text_monthly_charges.insert(Tkinter.INSERT, 'Monthly Plan\n  Charges\n')   
    text_lines = Tkinter.Text(frame_table, height = 8, width = 15, bd = 5)
    text_lines.insert(Tkinter.INSERT, '\n\n\n')   
    text_splitter = Tkinter.Text(window, height = 1, width = 30, bd = 5)
    text_splitter.insert(Tkinter.INSERT, '------------------------------')   
    text_total = Tkinter.Text(frame_total, height = 1, width = 15, bd = 5)
    text_total.insert(Tkinter.INSERT, 'TOTAL\t$%.2f' % get_total(lines))    
    text_copyright = Tkinter.Text(window, height = 1, width = 50, bd = 5)
    text_copyright.insert(Tkinter.INSERT, '© 2014 Yi Guo Programmed. ALL RIGHTS RESERVED!')   
    for line in lines:
        text_line_total.insert(Tkinter.END, '\n  $%.3f' % line.get_total())
        text_government_fees.insert(Tkinter.END, '\n   $%.3f' % line.charges.get('Government Fees Taxes'))
        text_surcharges.insert(Tkinter.END, '\n  $%2.3f' % line.charges.get('Surcharges And Fees'))
        text_usage_charges.insert(Tkinter.END, '\n  $%.3f' % line.charges.get('Talk Usage Charges'))
        text_monthly_charges.insert(Tkinter.END, '\n  $%.3f' % line.charges.get('Monthly Plan Charges'))
        text_lines.insert(Tkinter.END, '***-***-%s\n' % line.number[8:])   
    text_splitter.pack(anchor = Tkinter.SE)
    text_line_total.pack(side = Tkinter.RIGHT)
    text_government_fees.pack(side = Tkinter.RIGHT)
    text_surcharges.pack(side = Tkinter.RIGHT)
    text_usage_charges.pack(side = Tkinter.RIGHT)
    text_monthly_charges.pack(side = Tkinter.RIGHT)
    text_lines.pack(side = Tkinter.LEFT)
    frame_total.pack(anchor = Tkinter.SE)
    text_total.pack(anchor = Tkinter.E)
    text_copyright.pack(anchor = Tkinter.SW)   
    window.mainloop()

def main():
    lines = []
    bill = BeautifulSoup(get_bill(sys.argv[1], sys.argv[2]))
    period = bill.find('h3', 'float-left').text.strip().replace('Current Bill for ', '')
    for line in bill.find_all('div', 'PadLeft20 btnimg'):
        charges = dict()
        for charge in line.find_all(tabindex='-1'):
            name = charge['aria-labelledby']
            amount = float(charge.find('div', 'float-right accRow bold padRight20').text[1:])
            charges[name] = amount
        lines.append(Line(line['id'][-12:], charges))
    surcharges_difference = get_difference([line.charges.get('Surcharges And Fees') for line in lines])
    government_fees_difference = get_difference([line.charges.get('Government Fees Taxes') for line in lines])
    for line in lines:
        line.update_all(surcharges_difference, government_fees_difference)
    GUI(lines, period)
    
main()