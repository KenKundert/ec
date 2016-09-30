# computes and displays loop gain
# x register is taken to be frequency
=freq
88.3u "V/per" =Kdet   # gain of phase detector
9.07G "Hz/V" =Kvco    # gain of voltage controlled oscillator
2 =M                  # divide ratio of divider at output of VCO
8 =N                  # divide ratio of main divider
2 =F                  # divide ratio of prescaler
freq 2pi* "rads/s" =omega
Kdet Kvco* omega/ M/ =a
N F* =f
a f* =T
`Open loop gain = $a\nFeedback factor = $f\nLoop gain = $T`
quit
