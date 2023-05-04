list_content = '''
            <tr class="border_top">
              <td rowspan="2" align="center">{} = {}</td>
              <td>Ra</td><td>{}&deg</td>
            </tr>
            <tr><td>Dec</td><td>{}&deg</td></tr>
'''

src_content = '''
            <tr>
              <td colspan="2" style="text-align:right">{}</td><td>&Delta;={}&deg;</td>
            </tr>
'''

open_tbody = '''
            <tbody>
'''
end_tbody = '''
            </tbody>
'''

lle_content = '''
      <tr>
        <td colspan="2">
          <table class="td_title">
            <tr>
              <td id="lle">LAT LOW-ENERGY ANALYSIS</td>
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td valign="top" rowspan="1">
          <table class="results">
            <tr><th colspan="3"><b>SIGMA MAXIMUM</b></th></tr>
            <tbody>
            <tr>
              <td rowspan="2" align="center">
                SIGMA = {lle_ts_max}</td>
              <td>Ra</td><td>{lle_ra_max}&deg</td>
            </tr>
            <tr><td>Dec</td><td>{lle_dec_max}&deg</td></tr>
            <tr><td colspan="2">Nearby 4FGL sources</td><td>{lle_n_src}</td></tr>
            {lle_max_src_list}
            <tr><td colspan="2">Sun in this pixel?</td><td>{lle_sun}</td></tr>
            <tr><td colspan="2">Moon in this pixel?</td><td>{lle_moon}</td></tr>
            </tbody>
            <tr><th colspan="3"><b>LIST OF OTHER SIGMA &gt {sigma_cut}</b></th></tr>
            {lle_ts_list}
          </table>
        </td>
        <td>
          <table class="customers">
            <tr>
              <td align="center">
                <b>SIGMA MAP</b></td></tr>
            <tr>
              <td>
                <img src={lle_ts_map} alt="lle sigma map" width="100%">
              </td>
            </tr>
          </table>
        </td>
      </tr>
'''

lle_link_content = '''
              <td><a href="#lle">LLE Analysis</a></td>
'''

ts_count_map_content = '''
      <tr>
        <td valign="top" rowspan="1">
          <table class="results">
            <tr><th colspan="3"><b>TS MAXIMUM</b></th></tr>
            <tbody>
            <tr>
              <td rowspan="2" align="center">
                TS = {pgw_ts_max}</td>
              <td>Ra</td><td>{pgw_ra_max}&deg</td>
            </tr>
            <tr><td>Dec</td><td>{pgw_dec_max}&deg</td></tr>
            <tr><td colspan="2">Nearby 4FGL sources</td><td>{pgw_n_src}</td></tr>
            {pgw_max_src_list}
            <tr><td colspan="2">Sun in this pixel?</td><td>{pgw_sun}</td></tr>
            <tr><td colspan="2">Moon in this pixel?</td><td>{pgw_moon}</td></tr>
            </tbody>
          </table>
        </td>
        <td>
          <table class="customers">
            <tr>
              <td align="center">
                <b>TS MAP</b></td>
              <td align="center">
                <b>COUNT MAP</b></td>
            </tr>
            <tr>
              <td>
                <img src={pgw_ts_map} alt="ts map" width="100%">
              </td>
              <td>
                <img src={pgw_c_map} alt="count map" width="100%">
              </td>
            </tr>
          </table>
        </td>
      </tr>
'''

bayesian_ul_content = '''
           <tbody>
            <tr><td colspan="3"><b>BAYESIAN FLUX UB (CL={cl}%)</b></td></tr>
            <tr><td>Photon flux</td><td colspan="2">{ph_ul} e-7 ph cm<sup>-2</sup> s<sup>-1</sup></td></tr>
            <tr><td>Energy flux</td><td colspan="2">{ene_ul} e-10 erg cm<sup>-2</sup> s<sup>-1</sup></td></tr>
           </tbody>
'''
