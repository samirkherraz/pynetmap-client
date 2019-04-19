 gnuplot -e "set terminal png transparent size 800,400 font arial 18;
        set title 'test';
        set datafile separator ',';
        set xdata time;
        set timefmt '%Y%m%d%H%M';
        set format x '%H:%M';
        set xtics rotate by 45 offset -2,-2;
        set bmargin 3;
        set grid;
        set yrange [0:100];
        set palette model RGB maxcolors 3;
        set palette model RGB defined (0 '#999900', 1 '#009900', 2 '#cc0000');
        set cbrange [0:2];
        unset colorbox;
        plot '/tmp/pynetmap/nec-nodecmodule.state.history.disk.png.list' using 1:2:3 notitle with filledcurves above x1 fc palette;" > /tmp/pynetmap/graph.png