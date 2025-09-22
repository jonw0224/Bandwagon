echo Start >> /mnt/usbmain/Jonathan/Projects/Bandwagon/cron.log
date >> /mnt/usbmain/Jonathan/Projects/Bandwagon/cron.log
cd /mnt/usbmain/Jonathan/Projects/Bandwagon
python getstockquotes.py > detail.log
echo Stop >> /mnt/usbmain/Jonathan/Projects/Bandwagon/cron.log
date >> /mnt/usbmain/Jonathan/Projects/Bandwagon/cron.log
