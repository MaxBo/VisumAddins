import numpy as np

def expand_array(arr,
                 arr_zones=None,
                 n_zones=None,
                 zone_no=None,
                 fill_value=0):


    if arr_zones is None:
        try:
            arr_zones = arr.zones.array
        except AttributeError:
            raise AttributeError('no zone definition given')

    if n_zones is None:
        if zone_no is None:
            return arr.astype('f4')
        else:
            n_zones = len(zone_no)
    
    if zone_no is not None:
        # expand array and fill with fill_value
        if n_zones > len(arr):
            idx = zone_no.searchsorted(arr_zones)
            m = np.empty((n_zones, n_zones), dtype = 'f4')
            m.fill(fill_value)
            m_temp = np.empty((n_zones, len(arr)), dtype = 'f4')
            m_temp.fill(fill_value)
            m_temp[idx] = arr.astype('f4')
            m[:, idx] = m_temp
            return m
        else:
            idx = arr_zones.searchsorted(zone_no)
            return arr[idx][:, idx].astype('f4')

    # truncate matrix if shape is larger than the Number of Zones
    elif n_zones <= arr.shape[0]:
        sl = slice(0, n_zones)
        return arr[sl, sl].astype('f4')

    # expand matrix if shape is smaller than the Number of Zones
    elif n_zones > arr.shape[0]:
        m = np.empty((n_zones, n_zones), dtype = 'f4')
        m.fill(fill_value)
        sl = slice(0, arr.shape[0])
        m[sl, sl] = arr.astype('f4')
        return m
