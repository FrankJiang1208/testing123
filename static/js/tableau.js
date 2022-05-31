  let dashboard={'title':['Annual Competitors Map','Deed Competitors Map','Florida Annual Noncompetitors Map','Texas Annual Noncompetitors Map','West Annual Noncompetitors Map','Midwest Annual Noncompetitors Map','Southwest Annual Noncompetitors Map','Southeast Annual Noncompetitors Map','Northeast Annual Noncompetitors Map','Florida Deed Noncompetitors Map','Texas Deed Noncompetitors Map','West Deed Noncompetitors Map','Midwest Deed Noncompetitors Map','Southwest Deed Noncompetitors Map','Southeast Deed Noncompetitors Map','Northeast Deed Noncompetitors Map'],'url':['https://10az.online.tableau.com/t/aureusfg/views/AnnualCompetitorsMap_16479754740700/Dashboard1?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/AnnualCompetitorsMap_16479754740700/Dashboard1?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/FloridaCompetitorMap/FloridaCompetitorRegion?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/TexasCompetitorMap/TexasCompetitorRegion?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/WestCompetitorMap/WestCompetitorRegion?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/MidwestCompetitorMap/MidwestCompetitorRegion?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/SouthwestCompetitorMap/SouthwestCompetitorRegion?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/SoutheastCompetitorRegion/SoutheastCompetitorRegion?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/NortheastCompetitorMap_16473717812700/NortheastCompetitorRegion?:display_count=n&:showAppBanner=false&:origin=viz_share_link&:showVizHome=n','https://10az.online.tableau.com/t/aureusfg/views/FloridaNoncompetitorDeedMap/Dashboard1?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/Texas-deed/Dashboard1?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/WestDeedNoncompetitorMap/Dashboard1?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/MidwestDeedNoncompetitorMap/Dashboard1?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/SouthwestDeedNoncompetitorMap/Dashboard1?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/SoutheastDeedNoncompetitorMap/Dashboard1?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link','https://10az.online.tableau.com/t/aureusfg/views/NortheastDeedNoncompetitorMap/Dashboard1?:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link']}

  var containerDiv = document.getElementById("vizContainer");
  url = dashboard['url'][0];
  var viz = new tableau.Viz(containerDiv, url);
    
  function exportPDF() {
    viz.showExportPDFDialog();
  }
  
  function exportImage() {
    viz.showExportImageDialog();
  }
  
  function exportData() {
    viz.showExportDataDialog();
  }
  
  function revertAll() {
    workbook.revertAllAsync();
  }
  
  function refreshData() {
    viz.refreshDataAsync();
  }

  //////////////////////////////////////////////////////////////
  function toggleFullscreen(elem) {
    elem = elem || document.documentElement;
    if (!document.fullscreenElement && !document.mozFullScreenElement &&
      !document.webkitFullscreenElement && !document.msFullscreenElement) {
      if (elem.requestFullscreen) {
        elem.requestFullscreen();
      } else if (elem.msRequestFullscreen) {
        elem.msRequestFullscreen();
      } else if (elem.mozRequestFullScreen) {
        elem.mozRequestFullScreen();
      } else if (elem.webkitRequestFullscreen) {
        elem.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
      } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      }
    }
  }



dropdown=d3.select('#selDashboard')
for (i=0;i<16;i++){
  let op=dropdown.append('option').text(dashboard['title'][i])
  op.property('value',i)
}
d3.selectAll('#selDashboard').on("change",getDashboard);

function getDashboard(){
  let id=parseInt(dropdown.property('value'));
  var div=d3.select('#vizContainer').select('iframe').attr('src',dashboard['url'][id]+'&:size=1000,827&:embed=y&:showVizHome=n&:bootstrapWhenNotified=y&:apiID=host0#navType=1&navSrc=Parse')
  var title=d3.select('h1').text(dashboard['title'][id])
}
  //////////////////////////////////////////////////////////////


window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

});
