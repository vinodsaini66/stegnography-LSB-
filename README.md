# stegnography-LSB-
detect a hidden message (either text or image) in an image.and give an alert message for hidden content . we also retrive hidden message from image  

Run-
python LSBSteg.py encode -i En_imag/captain.jpg -o Stegno_imag/captain_stegno1.png -f En_Msg/new.txt

python LSBSteg.py decode -i Stegno_imag/captain_stegno1.png -o DE_msg/captain_msg.txt
