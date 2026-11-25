Output media/ulysses-demo.gif
Set Shell zsh
Set Theme "Catppuccin Mocha"
Set Width 1280
Set Height 740
Set FontSize 16
Set Padding 18
Set Framerate 10
Set PlaybackSpeed 6
Env PS1 "$ "
Hide
Type 'export PATH="$HOME/.local/bin:$PATH" && cd "$(git rev-parse --show-toplevel)" && clear' Enter
Show
Type "./demo" Enter
Wait+Line@900s /^\$$/
Sleep 60s
# The recorded GIF was then sped up 3x on its scrolling part with ffmpeg (hold kept at 10 s): recording time varied 4x with machine load.
