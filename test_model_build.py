import sys
sys.path.insert(0, '.')
from ultralytics.nn.tasks import parse_model
import yaml

d = yaml.safe_load(open('yolo11s_BSE.yaml'))
model, save = parse_model(d, ch=3, verbose=True)
print("\n=== Model built successfully! ===")
print(f"Total parameters: {sum(p.numel() for p in model.parameters())}")
