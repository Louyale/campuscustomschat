// Openly licensed photos from Wikimedia Commons, with author and license
// credits. Files live in public/photos/campus and public/photos/gear.

export interface Photo {
  src: string
  alt: string
  caption: string
  credit: string
  license: string
  source: string
}

export const CAMPUS_PHOTOS: Photo[] = [
  {
    src: '/photos/campus/harkness-tower.jpg',
    alt: 'Harkness Tower rising above Old Campus, framed by green tree branches against a pale sky',
    caption: 'Harkness Tower, framed in green',
    credit: 'Carol M. Highsmith',
    license: 'Public domain',
    source: 'https://commons.wikimedia.org/wiki/File:Harkness_Tower_Canopy_Highsmith.jpg',
  },
  {
    src: '/photos/campus/branford-autumn.jpg',
    alt: 'Bright orange and red autumn trees in the Branford College courtyard with Harkness Tower behind',
    caption: 'Branford College in full autumn color',
    credit: 'Anthony Tokman',
    license: 'CC BY-SA 4.0',
    source: 'https://commons.wikimedia.org/wiki/File:Branford_harkness.jpg',
  },
  {
    src: '/photos/campus/sterling-library.jpg',
    alt: 'Front view of the Gothic stone facade and central tower of Sterling Memorial Library',
    caption: 'Sterling Memorial Library, front and center',
    credit: 'Christian David',
    license: 'CC BY-SA 4.0',
    source: 'https://commons.wikimedia.org/wiki/File:Sterling_Memorial_Library_seen_from_the_front,_Yale_University,_New_Haven,_Connecticut.jpg',
  },
  {
    src: '/photos/campus/cross-campus-autumn.jpg',
    alt: 'Sunlit tree-lined walkway on Cross Campus with yellow fall leaves and Gothic buildings',
    caption: 'A golden fall stroll on Cross Campus',
    credit: 'Emilie Foyer',
    license: 'CC BY-SA 3.0',
    source: 'https://commons.wikimedia.org/wiki/File:Yale_University_Cross_Campus_2.jpg',
  },
  {
    src: '/photos/campus/beinecke-night.jpg',
    alt: 'The marble-paneled Beinecke Rare Book Library glowing from below at night',
    caption: 'Beinecke Library aglow after dark',
    credit: 'Nick Allen',
    license: 'CC BY-SA 3.0',
    source: 'https://commons.wikimedia.org/wiki/File:Beinecke_Library_at_night.JPG',
  },
  {
    src: '/photos/campus/old-campus-dusk.jpg',
    alt: 'Wide view of the Old Campus lawn and bare trees under a pink dusk sky',
    caption: 'Old Campus under a pink dusk sky',
    credit: 'Namkota',
    license: 'CC BY-SA 4.0',
    source: 'https://commons.wikimedia.org/wiki/File:Old_campus.jpg',
  },
  {
    src: '/photos/campus/davenport-snow.jpg',
    alt: 'Snow on the Davenport College courtyard lawn with red brick buildings and towers beyond',
    caption: 'Fresh snow in the Davenport courtyard',
    credit: 'Nick Allen',
    license: 'CC BY-SA 3.0',
    source: 'https://commons.wikimedia.org/wiki/File:Davenport_College_courtyard_2.JPG',
  },
  {
    src: '/photos/campus/yale-bowl-aerial.jpg',
    alt: 'Aerial view of the oval Yale Bowl stadium with the New Haven skyline in the distance',
    caption: 'The Yale Bowl from above',
    credit: 'Quintin Soloviev',
    license: 'CC BY 4.0',
    source: 'https://commons.wikimedia.org/wiki/File:Yale_Bowl_with_New_Haven_skyline.jpg',
  },
]

export const GEAR_PHOTOS: Photo[] = [
  {
    src: '/photos/gear/handsome-dan.jpg',
    alt: 'Handsome Dan, the Yale bulldog mascot, lying on grass wearing a blue bandana with a white Y',
    caption: 'Handsome Dan, rocking the Y',
    credit: 'Joeshmonobody',
    license: 'CC BY-SA 4.0',
    source: 'https://commons.wikimedia.org/wiki/File:Handsome_Dan_Kingman.jpg',
  },
  {
    src: '/photos/gear/football-team.jpg',
    alt: 'Yale football players in navy jerseys and white helmets jogging onto the field at the Yale Bowl',
    caption: 'Bulldogs taking the field at the Bowl',
    credit: 'Kenneth Zirkel',
    license: 'CC BY-SA 3.0',
    source: 'https://commons.wikimedia.org/wiki/File:2019_Yale_Bulldogs_football_players.jpg',
  },
  {
    src: '/photos/gear/cheerleaders.jpg',
    alt: 'Yale cheerleaders in navy and white uniforms with pom-poms on the field at the Yale Bowl',
    caption: 'Yale cheer bringing the game-day energy',
    credit: 'Kenneth Zirkel',
    license: 'CC BY-SA 3.0',
    source: 'https://commons.wikimedia.org/wiki/File:Yale_University_Cheerleaders.jpg',
  },
  {
    src: '/photos/gear/hockey-captain.jpg',
    alt: 'Yale hockey captain in a white YALE jersey and navy helmet skating during a game against Princeton',
    caption: 'Yale hockey, captain on the ice',
    credit: 'Amanda B',
    license: 'CC BY 2.0',
    source: 'https://commons.wikimedia.org/wiki/File:Yale_vs_Princeton_(6449969079).jpg',
  },
  {
    src: '/photos/gear/marching-band.jpg',
    alt: 'Yale Precision Marching Band members in navy jackets and chef hats playing brass and drums on the field',
    caption: 'The Yale band, chef hats and all',
    credit: 'Kenneth Zirkel',
    license: 'CC BY-SA 3.0',
    source: 'https://commons.wikimedia.org/wiki/File:Yale_Precision_Marching_Band_wearing_chef_hats.jpg',
  },
  {
    src: '/photos/gear/commencement-caps.jpg',
    alt: 'Yale graduates in black gowns and decorated caps walking in the Commencement procession on Old Campus',
    caption: 'Decorated caps on Commencement Day',
    credit: 'Dicklyon',
    license: 'CC BY-SA 4.0',
    source: 'https://commons.wikimedia.org/wiki/File:Yale_FES_caps.jpg',
  },
]
