#!/usr/bin/env gnuplot
set term pngcairo dashed enhanced
set output "/results/images/memorychart.png"


set xtics 10
#set ytics 30000

set grid ytics xtics


set format x "{%.0f}k"

#set size ratio 3
set xtics font "sans, 20pt" 
set ytics font "sans, 20pt"  nomirror
#set y2tics font "sans, 20pt" nomirror

set termoption dashed

set xtics offset 0,-0.1
#set tics out scale 3
#set y2tics autofreq
set ylabel "Memory (mb)" font "sans, 20pt"  offset -2,0
#set ylabel "Adapter Resident Set Size (kb)" font "sans, 20pt"   offset -3,0
set title "Memory Usage" font "sans, 20pt"
set xlabel "request number" font "sans, 20pt"
set style line 1 lc rgb '#000000' pt 1 ps 0.5 lt 1 lw 5 # --- red
set style line 2 lc rgb '#666666' pt 6 ps 0.5 lt 1 lw 5 # --- green
set style line 3 lc rgb '#BBBBBB' pt 5 ps 0.3 lt 1 lw 5 # --- red
set style line 4 lc rgb '#000000' pt 1 ps 0.5 lt 4 lw 4 dt 3 # --- red
set style line 5 lc rgb '#666666' pt 6 ps 0.5 lt 4 lw 4 dt 3 # --- green
set style line 6 lc rgb '#BBBBBB' pt 5 ps 0.5 lt 4 lw 4 dt 3 # --- red


set key left top
set key samplen 3
set key font "sans, 18pt"
set key spacing 1.1
set style data lines

set datafile separator "\t"
plot "/results/memory_evernote.tsv" using ($1/1000):($2/1024) title "Evernote" ls 1, \
     "/results/memory_twitter.tsv" using ($1/1000):($2/1024) title "Twitter" ls 2, \
     "/results/memory_twitter.tsv" using ($1/1000):($3/1024) notitle ls 5, \
     "/results/memory_chess.tsv" using ($1/1000):($2/1024) title "Chess" ls 3, \
     "/results/memory_chess.tsv" using ($1/1000):($3/1024) notitle ls 6, \
      "/results/memory_evernote.tsv" using ($1/1000):($3/1024) title "   Store Size" ls 4
     # "data/memory.tsv" using 1:4 ls 2 , \
     # "data/memory.tsv" using 1:5 ls 5 axes x1y2, \
     # "data/memory.tsv" using 1:6 ls 3, \
     # "data/memory.tsv" using 1:7 ls 6 axes x1y2



reset



set term pngcairo dashed enhanced
set output "/results/images/throughputchart.png"
#set xtics 250
#set ytics 5000

set format x "{%.0f}k"

set xtics 10

set grid
set xtics offset 0,-0.1
set xtics font "sans, 20pt" 
set yrange [0:100]
set y2range [0:100]
set ylabel "Latency (ms)" font "sans, 20pt"   offset -2,0
set ytics font "sans, 20pt"  nomirror
set title "Latency of Adapter" font "sans, 20pt"
set xlabel "request number" font "sans, 20pt"
set style line 1 lc rgb '#000000' pt 1 ps 1 lt 1 lw 4 # --- red
set style line 2 lc rgb '#666666' pt 6 ps 1 lt 1 lw 4 # --- green
set style line 3 lc rgb '#BBBBBB' pt 5 ps 1 lt 1 lw 4 # --- red
set key left top
set key samplen 3
set key font "sans, 18pt"
set key spacing 0.9

set datafile separator "\t"
plot "/results/timing_evernote.tsv" using ($1/1000):2 title "Evernote" ls 1, \
     "/results/timing_twitter.tsv" using ($1/1000):2 title "Twitter" ls 2, \
     "/results/timing_chess.tsv" using ($1/1000):2 title "Chess" ls 3
     # "data/memory.tsv" using 1:4 ls 5, \
     # "data/memory.tsv" using 1:6 ls 6



reset

set term pngcairo dashed enhanced size 480,530
set output "/results/images/networkchart.png"

unset xtics

set xtics offset 0,-0.5
set size ratio 1.2
set xtics format " "
set ytics format " "
set xtics ("Evernote" 10, "Twitter" 21.5, "Chess" 31)
set xrange [5:35]
set y2range [0:150]
set yrange [0:150]
unset grid
set grid y2tics

set xtics font "sans, 20pt" 
set y2tics font "sans, 20pt" 
set ytics 25 nomirror
set y2tics 25 nomirror
set title "Network Overhead" font "sans, 20pt"
set y2label "Traffic overhead per RPC (bytes)" font "sans, 20pt"  offset 3,0
unset key
plot "/results/network.tsv" with errorbars pt 3 lw 4 ps 4 lc rgb "black"
