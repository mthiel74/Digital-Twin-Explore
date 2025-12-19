import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Rectangle

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, help="JSONL log file")
    ap.add_argument("--out", default="msd_animation.gif", help="Output GIF file")
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()

    # Load data
    data = []
    with open(args.log, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    # Extract arrays
    times = [d['t'] for d in data]
    # msd model: x1 = position, x2 = velocity
    # x_true might be missing if we didn't log it, but run_twin_stream adds it
    
    # Let's handle cases where x_true might not be in the log (though it is in ours)
    x_true_pos = [d['x_true'][0] for d in data]
    x_hat_pos = [d['x_hat'][0] for d in data]
    
    # Measurements (noisy)
    y_meas = [d['y1'] for d in data]

    # Setup Plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(times[0], times[-1])
    # Auto-scale Y based on data + margin
    all_y = x_true_pos + x_hat_pos + y_meas
    min_y, max_y = min(all_y), max(all_y)
    margin = (max_y - min_y) * 0.2
    ax.set_ylim(min_y - margin, max_y + margin)
    
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Position (m)')
    ax.set_title('Digital Twin: Mass-Spring-Damper (True vs Estimated)')
    
    # Static elements (spring anchor)
    anchor_y = 0.0 # Equilibrium is roughly 0? No, let's assume 0 is equilibrium
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5, label='Equilibrium')

    # Lines for history
    line_true, = ax.plot([], [], 'b-', alpha=0.3, label='True Trajectory')
    line_hat, = ax.plot([], [], 'r--', alpha=0.6, label='Twin Estimate')
    line_meas, = ax.plot([], [], 'k.', alpha=0.1, markersize=2, label='Noisy Sensors')

    # Objects (The "Mass")
    # We'll plot them at a fixed Time X, moving up/down? 
    # Actually, usually animations move through time. 
    # Let's have a "Current Time" vertical line, and the mass moving on the right side panel?
    # Or just animate the point moving on the graph?
    # Let's do: Graph on left (scrolling?), System visual on right.
    
    # Re-setup for 2 subplots
    plt.clf()
    fig, (ax_graph, ax_viz) = plt.subplots(1, 2, figsize=(10, 5), gridspec_kw={'width_ratios': [2, 1]})
    
    # Graph Axis
    ax_graph.set_xlim(times[0], times[-1])
    ax_graph.set_ylim(min_y - margin, max_y + margin)
    ax_graph.set_xlabel('Time (s)')
    ax_graph.set_ylabel('Position')
    ax_graph.legend(loc='upper right')
    
    g_line_true, = ax_graph.plot([], [], 'b-', alpha=0.5, label='True')
    g_line_hat, = ax_graph.plot([], [], 'r--', label='Est')
    g_line_meas, = ax_graph.plot([], [], 'k.', alpha=0.2, markersize=2)
    g_time_line = ax_graph.axvline(times[0], color='k', alpha=0.5)

    # Viz Axis (Physical representation)
    ax_viz.set_xlim(-1, 1)
    ax_viz.set_ylim(min_y - margin, max_y + margin)
    ax_viz.set_xticks([])
    ax_viz.set_title("Physical View")
    
    # True Mass (Blue Box)
    rect_true = Rectangle((-0.4, 0), 0.3, 0.2, color='blue', alpha=0.5, label='True System')
    ax_viz.add_patch(rect_true)
    
    # Twin Mass (Red Ghost Box)
    rect_hat = Rectangle((0.1, 0), 0.3, 0.2, color='red', alpha=0.5, linestyle='--', fill=False, linewidth=2, label='Digital Twin')
    ax_viz.add_patch(rect_hat)
    
    # Springs (lines)
    spring_true, = ax_viz.plot([], [], 'b-', lw=1)
    spring_hat, = ax_viz.plot([], [], 'r--', lw=1)
    
    # Ceiling
    ceiling = 1.0 # arbitrary top anchor
    ax_viz.plot([-0.5, 0.5], [ceiling, ceiling], 'k-', lw=3)

    def init():
        g_line_true.set_data([], [])
        g_line_hat.set_data([], [])
        g_line_meas.set_data([], [])
        return g_line_true, g_line_hat, g_line_meas, rect_true, rect_hat, spring_true, spring_hat, g_time_line

    # Decimate data to match FPS if needed
    # total duration
    duration = times[-1] - times[0]
    total_frames = int(duration * args.fps)
    step = max(1, len(times) // total_frames)
    indices = range(0, len(times), step)

    def update(frame_idx):
        t = times[frame_idx]
        xt = x_true_pos[frame_idx]
        xh = x_hat_pos[frame_idx]
        
        # Update graph
        # Show history up to now
        current_times = times[:frame_idx+1]
        g_line_true.set_data(current_times, x_true_pos[:frame_idx+1])
        g_line_hat.set_data(current_times, x_hat_pos[:frame_idx+1])
        g_line_meas.set_data(current_times, y_meas[:frame_idx+1])
        g_time_line.set_xdata([t])

        # Update Viz
        # True Mass
        rect_true.set_y(xt - 0.1) # Center vertically
        spring_true.set_data([-0.25, -0.25], [ceiling, xt])
        
        # Twin Mass
        rect_hat.set_y(xh - 0.1)
        spring_hat.set_data([0.25, 0.25], [ceiling, xh])
        
        return g_line_true, g_line_hat, g_line_meas, rect_true, rect_hat, spring_true, spring_hat, g_time_line

    ani = animation.FuncAnimation(fig, update, frames=indices, init_func=init, blit=False, interval=1000/args.fps)
    
    print(f"Saving animation to {args.out} ...")
    ani.save(args.out, writer='pillow', fps=args.fps)
    print("Done.")

if __name__ == "__main__":
    main()
