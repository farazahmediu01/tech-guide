import time
import platform

def main():
    print("=" * 40)
    print("  Hello from inside a Docker container!")
    print("=" * 40)
    print(f"  Python version : {platform.python_version()}")
    print(f"  OS             : {platform.system()} {platform.release()}")
    print(f"  Architecture   : {platform.machine()}")
    print("=" * 40)

    # Simple loop to show the container is running
    for i in range(1, 11):
        print(f"  [{i}/10] Container is alive... ")
        time.sleep(1)

    print("\n  Done! Container finished successfully.")

if __name__ == "__main__":
    main()
