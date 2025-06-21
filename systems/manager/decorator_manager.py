
def error_message(file_path, name=None, raise_error=False):
    '''This will be used for messaging a useful error'''
    try:
        if not name and raise_error:
            raise NameError("Missing 'name' argument.")
    except NameError as e:
        print(f"\nERROR: {e}")
    finally:
        print(f"FILE PATH: {file_path}")
        if name:
            print(f"\nERROR: {name} on the directory path does not load")
        else:
            print("\nERROR: <unknown name> on the directory path does not load")
