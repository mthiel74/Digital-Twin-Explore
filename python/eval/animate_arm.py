import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, help="JSONL log file")
    ap.add_argument("--out", default="arm_animation.gif", help="Output GIF file")
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()

    # Parameters (should match model, hardcoded for visualization)
    l1 = 1.0
    l2 = 1.0

    # Load data
    data = []
    with open(args.log, 'r') as f:
        for line in f:
            data.append(json.loads(line))
            
    if not data:
        print("No data found.")
        return

    times = [d['t'] for d in data]
    
    # Extract joints: [q1, q2]
    # Check if 'joints' field exists
    if 'joints' not in data[0]:
        print("Log does not contain 'joints' field. Is this an arm run?")
        return

    q_list = [d['joints'] for d in data]
    q1 = np.array([q[0] for q in q_list])
    q2 = np.array([q[1] for q in q_list])
    
    # Measurements (End Effector X/Y were stored in x1, x2 by run_twin_stream)
    ee_x_meas = np.array([d.get('x1', 0) for d in data])
    ee_y_meas = np.array([d.get('x2', 0) for d in data])

    # Kinematics for visualization
    # Joint 1 (Elbow)
    x1_pos = l1 * np.cos(q1)
    y1_pos = l1 * np.sin(q1)
    
    # Joint 2 (End Effector)
    x2_pos = x1_pos + l2 * np.cos(q1 + q2)
    y2_pos = y1_pos + l2 * np.sin(q1 + q2)

    # Setup Plot
    fig, ax = plt.subplots(figsize=(6, 6))
    limit = (l1 + l2) * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_title("Digital Twin: 2-Link Robot Arm")

    # Elements
    line_arm, = ax.plot([], [], 'o-', lw=4, color='blue', label='Robot')
    line_trace, = ax.plot([], [], '-', lw=1, color='red', alpha=0.5, label='EE Trace')
    
    # Trace history
    trace_x, trace_y = [], []

    def init():
        line_arm.set_data([], [])
        line_trace.set_data([], [])
        return line_arm, line_trace

    # Decimate
    duration = times[-1] - times[0]
    total_frames = int(duration * args.fps)
    step = max(1, len(times) // total_frames)
    indices = range(0, len(times), step)

    def update(frame_idx):
        # Current coords
        x0, y0 = 0, 0
        x1, y1 = x1_pos[frame_idx], y1_pos[frame_idx]
        x2, y2 = x2_pos[frame_idx], y2_pos[frame_idx]
        
        # Update Arm
        line_arm.set_data([x0, x1, x2], [y0, y1, y2])
        
        # Update Trace
        # We append to local lists? Or just slice the precomputed arrays?
        # Slicing precomputed is faster/easier logic here
        # But we only want trace up to now.
        # Let's just append for simplicity in logic
        # trace_x.append(x2)
        # trace_y.append(y2)
        # Actually, using slicing is better for performance if array is large
        current_x = x2_pos[:frame_idx+1]
        current_y = y2_pos[:frame_idx+1]
        
        # Keep trace length reasonable? 
        # For now, full trace
        line_trace.set_data(current_x, current_y)
        
        return line_arm, line_trace

    ani = animation.FuncAnimation(fig, update, frames=indices, init_func=init, blit=True, interval=1000/args.fps)
    
    print(f"Saving animation to {args.out} ...")
    ani.save(args.out, writer='pillow', fps=args.fps)
    print("Done.")

if __name__ == "__main__":
    main()
