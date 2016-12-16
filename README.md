# TsAnalize
this application is used to analize a stream pcr/pts, and es data .

usage:
  ./TsRunngin [ts-file] [options --pts=[pid] --pcr=[pid] --dumpes=[pid]....]
  
there is there basic function

1. pts/pcr dump

  run below command can dump pcr/pts from given ts file
  
  ./TsRunning [ts_file] --pts=[pid] .....--pcr=[pid]...
  
2. es data dump

  run below command can dump es data from given ts file
  
    ./TsRuning [ts_file] --dumpes=[pid]....
    
3. pts/pcr show.

  after run pts/pcr dump. pts/pcr can be show with graphic
  
  open index.html in html5-svg-multi-line-chart, will show result in web browse
  
  this function only show last result of pcr/pts dump opteration
