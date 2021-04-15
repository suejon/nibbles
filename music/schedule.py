from background_task import background

@background(schedule=60)
def update_meta():
  print('scheduler triggered')
