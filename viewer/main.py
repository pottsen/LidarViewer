from canvas_and_window_dock import Window, Canvas
import vispy.app

def main():
    canvas = Canvas()
    canvas.window.show()
    vispy.app.run()

if __name__ == '__main__':
    import sys
    main()

