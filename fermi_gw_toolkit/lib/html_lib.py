list_content = '''
            <tr>
              <td rowspan="2" align="center">{}<br>{}</td>
              <td>Ra</td><td>{}&deg</td>
            </tr>
            <tr><td>Dec</td><td>{}&deg</td></tr>
'''

lle_content = '''
      <tr>
        <td colspan="2">
          <table class="td_title">
            <tr>
              <td>LLE ANALYSIS</td>
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td valign="top" rowspan="1">
          <table class="customers">
            <tr><td><b>SIGMA MAXIMUM</b><td></td><td></td></td></tr>
            <tr>
              <td rowspan="2" align="center">
                SIGMA<br>{lle_ts_max}</td>
              <td>Ra</td><td>{lle_ra_max}&deg</td>
            </tr>
            <tr><td>Dec</td><td>{lle_dec_max}&deg</td></tr>
            <tr><td colspan="3"></td></tr>
            <tr><td >LIST OF SIGMA &gt {sigma_cut}</td></tr>
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

pgw_content = '''
      <tr>
        <td valign="top" rowspan="1">
          <table class="customers">
            <tr><td><b>TS MAXIMUM</b><td></td><td ></td></td></tr>
            <tr>
              <td rowspan="2" align="center">
                TS<br>{ts_max}</td>
              <td>Ra</td><td>{ra_max}&deg</td>
            </tr>
            <tr><td>Dec</td><td>{dec_max}&deg</td></tr>
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
                <img src={ts_map} alt="ts map" width="100%">
              </td>
              <td>
                <img src={c_map} alt="count map" width="100%">
              </td>
            </tr>
          </table>
        </td>
      </tr>
'''

bayesian_ul_content = '''
           <table class="customers" >
            <tr><td colspan="3"><b>BAYESIAN UB (CL = {cl}%)</b></td></tr>
            <tr><td>Photon flux</td><td colspan="2">{ph_ul} e-7 ph cm<sup>-2</sup> s<sup>-1</sup></td></tr>
            <tr><td>Energy flux</td><td colspan="2">{ene_ul} e-10 erg cm<sup>-2</sup> s<sup>-1</sup></td></tr>
          </table>
'''
