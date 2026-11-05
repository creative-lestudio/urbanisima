#!/usr/bin/env python3
"""
Genera las páginas de servicios (/servicios/ y una página por servicio), el sitemap y las
redirecciones 301 de las URLs antiguas de WordPress.

Uso (desde la raíz del proyecto):   python3 scripts/build-services.py

Para cambiar un texto, edita SERVICES más abajo y vuelve a ejecutar el script.
Los textos parten de lo que ya decía la web antigua del cliente.
"""
import html, json, os, re, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SITE = 'https://grupo-urbanisima.com'
PHONE_TXT = '+34 722 115 251'
PHONE_TEL = '+34722115251'
WA = '34722115251'
MAIL = 'info@grupo-urbanisima.com'
V = '32'  # versión de CSS/JS (rompe la caché del navegador)

# ---------------------------------------------------------------- DATOS
# Lista oficial de servicios facilitada por el dueño (3/11/2026). Los 14 están disponibles para cualquier cliente;
# rank = (viviendas particulares, comunidades de vecinos, naves industriales): 1 = más probable que sea el servicio buscado.
SERVICES = [
 dict(key='tejados', slug='rehabilitacion-reparacion-tejados-valencia', icon='roof', rank=(2,5,4),
  title='Rehabilitación y reparación de tejados antiguos',
  short='Cambio de tejas, retejados y sustitución de uralita en tejados antiguos o deteriorados.',
  meta='Rehabilitación y reparación de tejados antiguos en Valencia: cambio de tejas, retejados, sustitución de uralita e impermeabilización. Presupuesto gratis.',
  intro='Rehabilitamos y reparamos tejados antiguos en toda la provincia de Valencia. Cambiamos tejas rotas o desplazadas, hacemos retejados, sustituimos uralita y resolvemos humedades y filtraciones para alargar la vida de la cubierta.',
  incluye=['Cambio de tejas de pizarra, tejas mixtas y otros tipos de teja','Retejados y recolocación de tejas desplazadas','Sustitución de uralita y de aislantes térmicos','Impermeabilización del tejado y sellado de filtraciones','Instalación de panel sandwich sobre la cubierta existente','Limpieza y mantenimiento de canalones y bajantes'],
  senales=['Tejas rotas, sueltas o desplazadas','Goteras o manchas de humedad en el techo','Cubierta antigua de uralita o muy deteriorada','Quieres alargar la vida del tejado sin construir uno nuevo'],
  faq=[('¿Cómo sé si hay que reparar o renovar la cubierta?','Depende del estado de las tejas, de la estructura y de la antigüedad de la cubierta. En la visita sin coste la revisamos y te explicamos si basta una reparación puntual o conviene una renovación.'),
       ('¿Cuánto cuesta rehabilitar un tejado?','Depende de la superficie, el material y el acceso. Por eso hacemos una visita sin coste y te damos un presupuesto sin compromiso.'),
       ('¿Trabajáis en comunidades de vecinos y naves industriales?','Sí. Atendemos a viviendas particulares, comunidades de vecinos y naves industriales en toda la provincia de Valencia.')],
  rel=['goteras','tejadosnuevos','impermeabilizacion'],
  bits=['Cambio de tejas y uralita','Retejados','Humedades y filtraciones']),
 dict(key='tejadosnuevos', slug='construccion-tejados-nuevos-valencia', icon='building', rank=(13,13,5),
  title='Construcción de tejados nuevos',
  short='Tejados nuevos para viviendas, edificios y naves, con los mejores materiales.',
  meta='Construcción de tejados nuevos en Valencia para viviendas, edificios y naves: montaje, impermeabilización y aislamiento. Presupuesto gratis y sin compromiso.',
  intro='Construimos tejados nuevos para viviendas, edificios y naves de la provincia de Valencia, con los mejores materiales y un acabado pensado para durar. Cuéntanos tu proyecto y te asesoramos en una visita sin coste.',
  incluye=['Montaje de tejados nuevos','Cubiertas de panel sandwich con aislamiento térmico y acústico','Impermeabilización y remates de la cubierta','Asesoramiento sobre los materiales más adecuados','Gestión de las licencias de obra cuando se necesitan','Plan de trabajo y de seguridad'],
  senales=['Vas a construir o ampliar una vivienda, un edificio o una nave','La cubierta está tan deteriorada que no compensa repararla','Quieres cambiar el tipo de cubierta'],
  faq=[('¿Me asesoráis sobre los materiales?','Sí. Te asesoramos sobre los materiales más adecuados según el uso, el edificio y tu presupuesto.'),
       ('¿Os encargáis de las licencias de obra?','Sí. Obtenemos y presentamos las licencias de obra oportunas cuando el proyecto las necesita.'),
       ('¿Cuánto cuesta un tejado nuevo?','Depende de la superficie, el tipo de cubierta y el acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['tejados','panel','impermeabilizacion'],
  bits=['Montaje de tejados nuevos','Aislamiento y remates','Licencias de obra']),
 dict(key='panel', slug='cubiertas-cerramientos-panel-sandwich-valencia', icon='layers', rank=(14,12,1),
  title='Cubiertas y cerramientos de panel sandwich',
  short='Cubiertas y cerramientos con aislamiento térmico y acústico, para naves y viviendas.',
  meta='Cubiertas y cerramientos de panel sandwich en Valencia: aislamiento térmico y acústico para naves industriales y viviendas. Presupuesto gratis y sin compromiso.',
  intro='Instalamos cubiertas y cerramientos de panel sandwich en toda la provincia de Valencia. Es una solución ideal tanto para naves industriales como para viviendas: impermeabiliza y aporta aislamiento térmico y acústico, resistente y duradero.',
  incluye=['Montaje de panel sandwich sobre la cubierta existente, formando una doble capa','Sustitución de la cubierta existente por placas de panel sandwich, evitando sobrepeso','Cerramientos de panel sandwich','Cubiertas de paneles de policarbonato','Rehabilitación y mantenimiento de paneles'],
  senales=['Cubierta de nave o vivienda con goteras o mal aislamiento','Problemas de temperatura o de ruido bajo la cubierta','Uralita o cubierta antigua que conviene sustituir','Necesitas cerrar o aislar una nave'],
  faq=[('¿Se puede instalar sobre la cubierta que ya tengo?','Sí, en muchos casos el panel sandwich se instala sobre la cubierta existente, formando una doble capa. También puede sustituirla para evitar sobrepeso. Lo valoramos en la visita.'),
       ('¿Sirve para viviendas o solo para naves?','Sirve para ambos: es una solución habitual en edificios industriales y también en viviendas.'),
       ('¿Cuánto cuesta instalar panel sandwich?','Depende de la superficie, el tipo de panel y el acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['tejadosnuevos','tejados','impermeabilizacion'],
  bits=['Doble capa o sustitución','Aislamiento térmico y acústico','Naves y viviendas']),
 dict(key='goteras', slug='reparacion-goteras-valencia', icon='drop', rank=(1,2,3),
  title='Reparación de goteras',
  short='Localizamos el origen y reparamos goteras, humedades y filtraciones de forma definitiva.',
  meta='Reparación de goteras en Valencia: localizamos el origen y damos una solución definitiva a goteras, humedades y filtraciones. Presupuesto gratis y sin compromiso.',
  intro='Localizamos el origen de las goteras y las reparamos de forma definitiva en tejados, terrazas, azoteas y cubiertas. Damos solución a goteras, humedades y filtraciones de todo tipo en la provincia de Valencia.',
  incluye=['Localización del origen de la gotera','Reparación de tejas, juntas y remates','Impermeabilización de la zona afectada','Tratamiento de humedades y filtraciones','Revisión de canalones y bajantes','Trabajos en altura, con o sin andamios'],
  senales=['Entra agua o hay goteras cuando llueve','Manchas de humedad en techos o paredes','Pintura que se levanta o desconcha','La gotera reaparece tras una reparación anterior'],
  faq=[('¿Por qué vuelve la gotera si ya la reparé?','Si no se localiza el origen real de la filtración, la humedad sigue entrando y provoca daños mayores. Hay que tratar la causa y no solo la mancha.'),
       ('¿Es urgente?','Si entra agua, conviene actuar cuanto antes para evitar daños mayores. Llámanos y valoramos la urgencia.'),
       ('¿Cuánto cuesta reparar una gotera?','Depende del origen, la superficie y el acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['impermeabilizacion','tejados','canalones'],
  bits=['Localizamos el origen','Reparación definitiva','Tejados y terrazas']),
 dict(key='terrazas', slug='rehabilitacion-construccion-terrazas-valencia', icon='floor', rank=(5,4,11),
  title='Rehabilitación y construcción de terrazas',
  short='Rehabilitamos terrazas y azoteas deterioradas y construimos terrazas nuevas, bien impermeabilizadas.',
  meta='Rehabilitación y construcción de terrazas en Valencia: reparación de azoteas y terrados e impermeabilización transitable. Presupuesto gratis y sin compromiso.',
  intro='Rehabilitamos terrazas, azoteas y terrados deteriorados y construimos terrazas nuevas, con la impermeabilización adecuada para que no entre la humedad. Trabajamos en viviendas y edificios de toda la provincia de Valencia.',
  incluye=['Rehabilitación de terrazas, azoteas y terrados','Construcción de terrazas nuevas','Reparación de grietas, fisuras y zonas deterioradas','Impermeabilización con resinas reforzadas con fibra de vidrio, transitables','Tratamiento de juntas, remates y desagües'],
  senales=['Suelo de la terraza agrietado, desgastado o con charcos','Humedad en los techos bajo la terraza','Quieres construir o ampliar una terraza','La terraza ya se reparó pero sigue entrando agua'],
  faq=[('¿Se puede seguir usando la terraza?','La impermeabilización con resina reforzada con fibra de vidrio es transitable. Te indicamos los plazos concretos en el presupuesto.'),
       ('¿Rehabilitar o construir una terraza nueva?','Depende del estado del soporte y de lo que necesites. En la visita sin coste lo valoramos y te proponemos la mejor opción.'),
       ('¿Cuánto cuesta?','Depende de la superficie y del estado actual. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['impermeabilizacion','goteras','fachadas'],
  bits=['Azoteas y terrados','Terrazas nuevas','Impermeabilización transitable']),
 dict(key='impermeabilizacion', slug='impermeabilizacion-cubiertas-canalones-terrazas-valencia', icon='shield', rank=(3,1,2),
  title='Impermeabilización de cubiertas, canalones y terrazas',
  short='Resinas reforzadas con fibra de vidrio para cubiertas, canalones y terrazas. Fin de goteras y filtraciones.',
  meta='Impermeabilización de cubiertas, canalones y terrazas en Valencia con resinas reforzadas con fibra de vidrio. Soluciones a goteras y humedades. Presupuesto gratis.',
  intro='Acabamos con las goteras, humedades y filtraciones en cubiertas, canalones, terrazas, azoteas y tejados. Una impermeabilización bien hecha evita que el agua siga entrando y que el daño llegue a la estructura del edificio.',
  incluye=['Revisión de la cubierta, el canalón o la terraza y localización del origen de la filtración','Reparación de grietas, fisuras y zonas deterioradas','Impermeabilización con resinas reforzadas con fibra de vidrio: flexibles, resistentes a la intemperie y transitables','Impermeabilización y reparación de canalones','Tratamiento de juntas, remates, bajantes y desagües','Impermeabilización de cubiertas de naves industriales'],
  senales=['Humedad o manchas en techos y paredes','Charcos que se acumulan o pintura que se levanta','Grietas o fisuras en el suelo de la terraza o la azotea','Goteras que reaparecen tras reparaciones anteriores'],
  faq=[('¿Qué es una impermeabilización con resina reforzada con fibra de vidrio?','Es un revestimiento continuo y flexible que se aplica sobre la superficie y la protege del agua. Resiste la intemperie, es transitable y no suele requerir grandes obras. En la visita valoramos si es la solución adecuada en tu caso.'),
       ('¿Por qué vuelve a entrar el agua si ya reparé la zona?','Si la impermeabilización no se hace correctamente, la humedad sigue entrando y provoca daños mayores. Hay que localizar el origen real de la filtración y tratar toda la superficie y los remates.'),
       ('¿Cuánto cuesta impermeabilizar?','Depende de la superficie, el estado del soporte y los remates. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['goteras','terrazas','tejados'],
  bits=['Resinas con fibra de vidrio','Cubiertas, canalones y terrazas','Fin de goteras y humedades']),
 dict(key='reforma', slug='reforma-integral-valencia', icon='home', rank=(8,8,7),
  title='Reforma integral',
  short='Reformas integrales de viviendas, pisos, casas y locales, con presupuesto consensuado.',
  meta='Reforma integral en Valencia de viviendas, pisos, casas y locales: albañilería, fontanería, electricidad, pintura y más. Presupuesto gratis y sin compromiso.',
  intro='Realizamos reformas integrales de viviendas, pisos, casas y locales comerciales. Planificamos presupuestos consensuados según las necesidades de cada cliente, te asesoramos en cada paso del proyecto y damos garantía de nuestro trabajo.',
  incluye=['Reformas integrales de viviendas, pisos, casas y locales comerciales','Albañilería, alicatados y solados','Fontanería y electricidad','Puertas, ventanas y cerramientos','Trabajos en pladur y escayola','Pintura interior'],
  senales=['Vivienda o local que necesita renovarse por completo','Instalaciones antiguas de agua o electricidad','Quieres una reforma con un único interlocutor y comunicación constante'],
  faq=[('¿Cómo se plantea el presupuesto de una reforma?','Planificamos presupuestos consensuados en función de las necesidades de cada cliente, tras una visita sin coste.'),
       ('¿Os encargáis de todos los gremios?','Sí. Contamos con profesionales de los distintos gremios y los coordinamos para que la reforma avance según los plazos acordados.'),
       ('¿Dais garantía del trabajo?','Sí. Los trabajos cuentan con la garantía legal que corresponde y con la que se indique en el presupuesto.')],
  rel=['banos','pladur','pinturainterior'],
  bits=['Viviendas y locales','Presupuesto consensuado','Todos los gremios']),
 dict(key='pladur', slug='trabajos-pladur-valencia', icon='layers', rank=(12,9,8),
  title='Trabajos en pladur',
  short='Tabiques, techos y revestimientos de pladur para reformas de viviendas, locales y naves.',
  meta='Trabajos en pladur en Valencia: tabiques, techos y revestimientos para viviendas, locales y naves. Presupuesto gratis y sin compromiso.',
  intro='Realizamos trabajos en pladur para reformas de viviendas, locales y naves: tabiques, techos y revestimientos, con un acabado limpio y coordinado con el resto de gremios de la reforma.',
  incluye=['Tabiques de pladur','Techos y falsos techos','Revestimientos de pladur y escayola','Trabajos coordinados con albañilería, electricidad y pintura','Asesoramiento sobre materiales y distribución de espacios'],
  senales=['Quieres dividir o redistribuir una estancia','Necesitas renovar o rebajar un techo','Estás haciendo una reforma y necesitas el trabajo de pladur'],
  faq=[('¿Hacéis solo pladur o la reforma completa?','Hacemos ambas cosas: trabajos de pladur sueltos o dentro de una reforma integral con los demás gremios.'),
       ('¿Me asesoráis sobre la distribución?','Sí. Te asesoramos sobre los materiales más adecuados y la distribución más óptima de los espacios.'),
       ('¿Cuánto cuesta?','Depende de los metros y del tipo de trabajo. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['reforma','banos','pinturainterior'],
  bits=['Tabiques y techos','Revestimientos','Dentro de tu reforma']),
 dict(key='banos', slug='reforma-banos-valencia', icon='drop', rank=(7,10,12),
  title='Reforma de baños',
  short='Reformas de baños completas o parciales: alicatados, fontanería, electricidad y pintura.',
  meta='Reforma de baños en Valencia, completa o parcial: alicatados y solados, fontanería, electricidad y pintura. Presupuesto gratis y sin compromiso.',
  intro='Reformamos baños completos o de forma parcial: alicatados y solados, fontanería, electricidad, puertas y pintura, con un único interlocutor y comunicación constante durante toda la obra.',
  incluye=['Reforma completa o parcial del baño','Alicatados y solados','Fontanería y electricidad','Puertas y ventanas','Trabajos de albañilería y pladur','Pintura'],
  senales=['Baño anticuado o con desperfectos','Instalaciones de fontanería antiguas o con fugas','Quieres renovar el baño sin complicaciones'],
  faq=[('¿Hacéis reformas parciales de un baño?','Sí. Podemos reformar el baño completo o solo una parte: suelos, alicatados, fontanería o lo que necesites.'),
       ('¿Cómo se presupuesta?','Tras una visita sin coste, te damos un presupuesto consensuado en función de tus necesidades.'),
       ('¿Cuánto cuesta reformar un baño?','Depende de los metros, los materiales y el alcance. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['reforma','pladur','pinturainterior'],
  bits=['Completa o parcial','Alicatados y fontanería','Electricidad y pintura']),
 dict(key='chimeneas', slug='limpieza-mantenimiento-chimeneas-valencia', icon='flame', rank=(6,11,13),
  title='Limpieza y mantenimiento de chimeneas',
  short='Deshollinado y revisión periódica de chimeneas: hollín, creosota y cenizas fuera.',
  meta='Limpieza y mantenimiento de chimeneas en Valencia: deshollinado, eliminación de hollín y creosota y prevención de incendios. Presupuesto gratis y sin compromiso.',
  intro='Una chimenea mal mantenida supone un riesgo de incendio. La combustión de la leña genera hollín, creosota y cenizas que se acumulan en la chimenea y en el conducto de humos. Limpiarla protege frente a incendios y también frente a intoxicaciones.',
  incluye=['Limpieza y deshollinado de la chimenea y del conducto de humos','Eliminación de hollín, creosota, cenizas y suciedad','Revisión periódica de la chimenea','Recomendaciones de uso y mantenimiento'],
  senales=['Llevas tiempo sin limpiar la chimenea','Olor a humo o a quemado, o hollín acumulado','Vas a empezar la temporada de uso'],
  faq=[('¿Por qué es importante limpiar la chimenea?','La creosota acumulada aumenta el riesgo de incendio y, si el conducto está obstruido, los gases pueden quedarse dentro de la vivienda, lo que resulta peligroso.'),
       ('¿Qué puedo hacer yo para cuidarla?','Limpiar las cenizas del hogar con regularidad y quemar solo leña adecuada. Aun así, conviene no renunciar al mantenimiento por parte de un profesional.'),
       ('¿Cuánto cuesta?','Depende del tipo de chimenea y del acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['desatasco','canalones','tejados'],
  bits=['Hollín y creosota','Prevención de incendios','Revisión periódica']),
 dict(key='desatasco', slug='desatasco-chimeneas-salidas-humo-valencia', icon='flame', rank=(11,14,14),
  title='Desatasco de chimeneas y salidas de humo',
  short='Desatascamos chimeneas y salidas de humo obstruidas para que vuelvan a funcionar con seguridad.',
  meta='Desatasco de chimeneas y salidas de humo en Valencia: eliminamos obstrucciones y residuos para evitar riesgos. Presupuesto gratis y sin compromiso.',
  intro='Si el humo no sale bien o el conducto está obstruido, los gases pueden quedarse dentro de la vivienda, lo que resulta peligroso. Desatascamos chimeneas y salidas de humo para que vuelvan a funcionar con seguridad.',
  incluye=['Desatasco de chimeneas y conductos de humos obstruidos','Eliminación de hollín, creosota y residuos acumulados','Revisión de la salida de humos','Recomendaciones para evitar nuevas obstrucciones'],
  senales=['El humo no sale bien o vuelve a la vivienda','Olor a humo en el interior','La chimenea o la salida de humos parece obstruida'],
  faq=[('¿Es peligroso un conducto obstruido?','Con el conducto obstruido, los gases se quedan en el interior de la vivienda, lo que puede ser un peligro para quienes estén dentro. Conviene revisarlo cuanto antes.'),
       ('¿Os encargáis también del mantenimiento?','Sí. Además del desatasco, realizamos limpieza y mantenimiento periódico de chimeneas.'),
       ('¿Cuánto cuesta?','Depende del tipo de instalación y del acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['chimeneas','tejados','canalones'],
  bits=['Chimeneas obstruidas','Salidas de humo','Seguridad en casa']),
 dict(key='canalones', slug='limpieza-canalones-valencia', icon='gutter', rank=(4,6,6),
  title='Limpieza de canalones',
  short='Limpieza y mantenimiento de canalones, canaletas y bajantes de todo tipo.',
  meta='Limpieza y mantenimiento de canalones, canaletas y bajantes en Valencia: aluminio, zinc, cobre y galvanizados. Presupuesto gratis y sin compromiso.',
  intro='Limpiamos y mantenemos canalones pluviales, canaletas y bajantes de todo tipo: aluminio, zinc, cobre o galvanizados. Un canalón obstruido o en mal estado es una de las causas más habituales de filtraciones en cubiertas y tejados. Todo el equipo cumple la normativa de prevención de riesgos laborales.',
  incluye=['Limpieza de canalones, canaletas y bajantes','Mantenimiento y revisión periódica','Canalones de aluminio, zinc, cobre y galvanizados','Sistemas antipájaros','Impermeabilización y reparación de canalones'],
  senales=['Canalones que desbordan o gotean cuando llueve','Hojas, barro o suciedad acumulados','Canalones oxidados, deformados o despegados','Manchas de humedad en la fachada bajo el canalón'],
  faq=[('¿Cada cuánto conviene limpiar los canalones?','Conviene revisarlos antes de la temporada de lluvias y después de temporales, sobre todo si hay árboles cerca, que acumulan hojas y suciedad.'),
       ('¿Hacéis el trabajo con andamio?','Hacemos trabajos en altura con o sin andamios, según lo que requiera cada caso.'),
       ('¿Cuánto cuesta limpiar un canalón?','Depende de la longitud, el material y el acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['impermeabilizacion','goteras','tejados'],
  bits=['Limpieza y bajantes','Mantenimiento periódico','Aluminio, zinc y cobre']),
 dict(key='pinturainterior', slug='pintura-interior-valencia', icon='palette', rank=(9,7,10),
  title='Pintura interior',
  short='Pintura interior completa o parcial de viviendas, chalets, portales y comunidades.',
  meta='Pintura interior en Valencia para viviendas, chalets y comunidades: plástica, alisados, estucos, quitar gotelé y lacados. Presupuesto gratis y sin compromiso.',
  intro='Desarrollamos proyectos de pintura interior completos, parciales y de obra nueva en viviendas, chalets y comunidades de vecinos. Contamos con asesoramiento de decoración y pintura, y con materiales de primera calidad.',
  incluye=['Pintura plástica, alisados y estucos','Quitar gotelé','Colocación de papel pintado y vinilos decorativos','Imitaciones, barnizados y lacados de puertas y muebles','Pintura de portales: techos, paredes, escaleras, rellanos, barandillas y puertas','Asesoramiento en decoración y pintura'],
  senales=['Paredes o techos con manchas, desconchones o gotelé','Quieres renovar una estancia o dar un toque moderno a tu hogar','Portal o zonas comunes de la comunidad que necesitan una mano de pintura'],
  faq=[('¿Pintáis solo una parte de la vivienda?','Sí. Realizamos proyectos completos, parciales y de obra nueva, desde una estancia hasta la vivienda entera.'),
       ('¿Me asesoráis con los colores y los acabados?','Sí. Contamos con asesoramiento de decoración y pintura para ayudarte a elegir.'),
       ('¿Cuánto cuesta pintar una vivienda?','Depende de los metros, el estado de las paredes y los acabados. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['fachadas','reforma','pladur'],
  bits=['Plástica, alisados y estucos','Gotelé, papel y vinilos','Barnizados y lacados']),
 dict(key='fachadas', slug='pintura-fachadas-valencia', icon='brush', rank=(10,3,9),
  title='Pintura de fachadas',
  short='Pintura y rehabilitación de fachadas, patios interiores y portales, con o sin andamios.',
  meta='Pintura de fachadas en Valencia: fachadas, patios interiores, portales, casas y chalets. Trabajos verticales sin andamio. Presupuesto gratis y sin compromiso.',
  intro='Pintamos fachadas, patios interiores, portales, casas y chalets. Como especialistas en trabajos verticales, accedemos sin andamios a los puntos más difíciles, de forma rápida, segura y sin molestar a propietarios e inquilinos.',
  incluye=['Pintura exterior y rehabilitación de fachadas','Pintura y restauración de patios interiores','Pintura de portales y zonas comunes','Pintura exterior de casas y chalets','Trabajos con andamio o con descuelgue vertical','Materiales con certificado de calidad de los fabricantes'],
  senales=['Pintura de la fachada desconchada, sucia o descolorida','Humedades, grietas o desprendimientos en la fachada','Patio interior deteriorado o con manchas','Quieres renovar el aspecto de tu casa o de tu comunidad'],
  faq=[('¿Hace falta montar andamios?','No siempre. Con trabajos verticales (descuelgue) accedemos a muchos puntos sin andamio, con menos molestias para los vecinos. Lo valoramos en la visita sin coste.'),
       ('¿Qué materiales utilizáis?','Materiales de primera calidad, con certificado de calidad de los fabricantes, para garantizar un buen acabado.'),
       ('¿Cuánto cuesta pintar una fachada?','Depende de la superficie, la altura, el estado del soporte y el tipo de acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['pinturainterior','impermeabilizacion','terrazas'],
  bits=['Fachadas y patios','Portales y comunidades','Con o sin andamios']),
]
BY_KEY = {s['key']: s for s in SERVICES}
PROBLEMS = [  # icono, título, subtítulo, servicio al que lleva
 ('drop', 'Goteras en el techo', 'Humedades y filtraciones', 'goteras'),
 ('roof', 'Tejado deteriorado', 'Tejas rotas o cubierta antigua', 'tejados'),
 ('shield', 'Terraza con humedades', 'Impermeabilización', 'impermeabilizacion'),
 ('gutter', 'Canalones obstruidos', 'Limpieza y mantenimiento', 'canalones'),
 ('brush', 'Fachada deteriorada', 'Pintura y rehabilitación', 'fachadas'),
 ('layers', 'Cubierta de nave', 'Panel sandwich y cerramientos', 'panel'),
 ('flame', 'Chimenea', 'Limpieza y desatasco', 'chimeneas'),
 ('home', 'Reforma', 'Integral, baños y pladur', 'reforma'),
]

# Redirecciones 301: URL antigua de WordPress -> página nueva (sin barra inicial ni final)
OLD = {
 'tejados': ['rehabilitacion-de-tejados-en-valencia','reparacion-de-tejados-en-valencia','reparacion-y-rehabilitacion-de-cubiertas-en-valencia','reparacion-cubiertas-naves-industriales-valencia','servicios-grupo-urbanisima/servicios-de-reparacion-de-tejados'],
 'impermeabilizacion': ['impermeabilizacion-de-tejados-en-valencia','impermeabilizacion-de-terrazas-en-valencia','impermeabilizacion-de-cubiertas-en-valencia','especialistas-en-impermeabilizacion-en-valencia','impermeabilizacion-de-cubiertas-valencia','impermeabilizacion-y-reparacion-de-canalones','servicios-grupo-urbanisima/servicios-de-impermeabilizacion-de-cubiertas','servicios-grupo-urbanisima/servicios-de-impermeabilizacion-de-terrazas'],
 'terrazas': ['rehabilitacion-de-terrazas-en-valencia'],
 'canalones': ['instalacion-y-montaje-de-canalones-en-valencia','limpieza-y-mantenimiento-de-canalones','servicios-grupo-urbanisima/servicios-de-limpieza-de-canalones'],
 'panel': ['instalacion-y-montaje-de-panel-sandwich','servicios-grupo-urbanisima/servicios-de-montaje-de-panel-sandwich'],
 'chimeneas': ['limpieza-y-deshollinado-de-chimenea-en-valencia','limpieza-y-deshollinado-de-chimenea-en-alicante','limpieza-y-deshollinado-de-chimenea-en-castellon','especialistas-en-deshollinar-chimeneas','deshollinacion-de-chimeneas-en-alicante','deshollinacion-de-chimeneas-en-castellon','servicios-grupo-urbanisima/servicio-de-limpieza-y-deshollinado-de-chimenea'],
 'fachadas': ['servicios-grupo-urbanisima/servicios-de-pintores-de-fachadas-y-patios-interiores'],
 'pinturainterior': ['servicios-grupo-urbanisima/servicios-de-pintores-de-casas-y-chalets-particulares-en-valencia'],
 'reforma': ['servicios-grupo-urbanisima/servicios-de-reformas','reformas-integrales-de-locales-valencia'],
}
OTHER_REDIRECTS = {  # destino directo
 'servicios-grupo-urbanisima': '/servicios/',
 'contactar': '/?ir=contacto',
 'servicios-a-particulares': '/?perfil=particulares&ir=servicios',
 'servicios-a-comunidades-de-vecinos': '/?perfil=comunidades&ir=servicios',
 'servicios-a-empresas-comercios-y-naves-industriales': '/?perfil=empresas&ir=servicios',
 # Servicios que ya no se ofrecen (lista del dueño, 3/11/2026): van al listado de servicios
 'servicios-grupo-urbanisima/servicio-de-pintura-epoxi-en-pavimento-continuo': '/servicios/',
 'servicios-grupo-urbanisima/servicios-de-jardineria': '/servicios/',
 'diseno-de-jardines-valencia': '/servicios/',
 'servicios-grupo-urbanisima/servicios-de-rehabilitacion-y-limpieza-de-piscinas-en-valencia': '/servicios/',
}
# Aire acondicionado: la web nueva no lo incluye. Mientras el cliente decide, va a la portada.
OLD_AC = ['recarga-de-aires-acondicionados-en-valencia','servicios-grupo-urbanisima/recarga-de-aires-acondicionados','servicios-de-montaje-e-instalacion-de-aire-acondicionado-en-valencia','reparacion-de-aire-acondicionado-en-valencia']

# ---------------------------------------------------------------- PLANTILLAS
e = html.escape
def ic(name, root, cls='i'): return f'<svg class="{cls}"><use href="{root}assets/icons.svg#i-{name}"/></svg>'

def head(title, desc, canonical, root, extra=''):
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="Grupo Urbanísima">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta name="theme-color" content="#01335a">
<link rel="icon" href="{root}assets/logo.png">
<link rel="preload" href="{root}assets/fonts/montserrat-latin-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}assets/fonts/fonts.css">
<style>.i{{width:1.15em;height:1.15em;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}}.skip{{position:absolute;left:-999px;top:8px}}</style>
<link rel="stylesheet" href="{root}styles.css?v={V}">
<script src="{root}config.js?v={V}"></script>
<script src="{root}tracking.js?v={V}" defer></script>
<script src="{root}pages.js?v={V}" defer></script>
{extra}</head>
'''

def header(root):
    return f'''<a class="skip" href="#contenido">Saltar al contenido</a>
<header class="header solid" id="top">
  <div class="wrap nav">
    <a href="{root}" class="brand" aria-label="Grupo Urbanísima, inicio"><img class="logo-color" src="{root}assets/logo.png" alt="" width="268" height="55"><img class="logo-white" src="{root}assets/logo-blanco.png" alt="" width="260" height="51"></a>
    <nav id="menu" class="menu" aria-label="Principal">
      <a href="{root}">Inicio</a>
      <a href="{root}servicios/">Servicios</a>
      <a href="#contacto">Contacto</a>
      <a href="tel:{PHONE_TEL}" class="menu-phone">{ic('phone',root)}722 115 251</a>
      <a href="#contacto" class="btn btn-sm" data-cta="header">Presupuesto gratuito</a>
    </nav>
    <button class="burger" aria-label="Abrir menú" aria-expanded="false" aria-controls="menu"><span></span><span></span></button>
  </div>
</header>
'''

RGPD = '''<details class="rgpd"><summary>Información básica sobre protección de datos</summary>
        <dl>
          <dt>Responsable</dt><dd>Grupo Urbanisima S.L.U.</dd>
          <dt>Finalidad</dt><dd>Atender tu solicitud de presupuesto o consulta.</dd>
          <dt>Legitimación</dt><dd>Tu consentimiento y las medidas precontractuales que nos pides.</dd>
          <dt>Destinatarios</dt><dd>No cedemos datos a terceros salvo obligación legal. Usamos proveedores de alojamiento y correo y, si eliges WhatsApp, esa plataforma (Meta). Con WhatsApp también recibimos una copia por correo.</dd>
          <dt>Derechos</dt><dd>Acceso, rectificación, supresión, oposición, limitación y portabilidad, escribiendo a info@grupo-urbanisima.com. Puedes reclamar ante la AEPD.</dd>
          <dt>Más información</dt><dd><a href="{root}ley-proteccion-datos/" target="_blank" rel="noopener">Política de privacidad</a></dd>
        </dl>
      </details>'''

def contact_section(root, heading, service_title=None):
    if service_title:
        svc = f'<input type="hidden" name="servicio" value="{e(service_title)}">'
    else:
        opts = ''.join(f'<option>{e(s["title"])}</option>' for s in SERVICES)
        svc = f'<div class="field"><label for="c-serv">¿Qué necesitas?</label><select id="c-serv" name="servicio"><option value="">Selecciona un servicio</option>{opts}<option>Otro</option></select></div>'
    return f'''<section class="section contact" id="contacto">
  <div class="wrap split">
    <div class="contact-copy">
      <p class="eyebrow">Contacto</p>
      <h2>{e(heading)}</h2>
      <p class="lead">Visita a domicilio sin coste y presupuesto sin compromiso, en toda la provincia de Valencia. Te respondemos en menos de 24 horas.</p>
      <ul class="contact-list">
        <li><a href="tel:{PHONE_TEL}"><span class="ico">{ic('phone',root)}</span><span><small>Llámanos</small>{PHONE_TXT}</span></a></li>
        <li><a href="https://wa.me/{WA}?text=Hola%2C%20quiero%20pedir%20presupuesto" target="_blank" rel="noopener"><span class="ico">{ic('chat',root)}</span><span><small>WhatsApp</small>Escríbenos ahora</span></a></li>
        <li><a href="mailto:{MAIL}"><span class="ico">{ic('mail',root)}</span><span><small>Email</small>{MAIL}</span></a></li>
        <li><span class="row"><span class="ico">{ic('clock',root)}</span><span><small>Atención telefónica</small>Lunes a viernes, de 9:00 a 19:00</span></span></li>
      </ul>
    </div>
    <form class="card" id="contact-form" novalidate>
      <div class="card-head"><h2>Cuéntanos qué necesitas</h2><p>Elige cómo quieres enviarlo: por correo o por WhatsApp.</p></div>
      <div class="field"><label for="c-nombre">Nombre</label><input id="c-nombre" name="nombre" type="text" autocomplete="name" placeholder="Tu nombre" required></div>
      <div class="field-row">
        <div class="field"><label for="c-tel">Teléfono</label><input id="c-tel" name="telefono" type="tel" autocomplete="tel" inputmode="tel" placeholder="6XX XXX XXX" required></div>
        <div class="field"><label for="c-email">Correo <small>(opcional)</small></label><input id="c-email" name="email" type="email" autocomplete="email" inputmode="email" placeholder="tu@correo.com"></div>
      </div>
      <div class="field"><label for="c-perfil">Soy <small>(opcional)</small></label>
        <select id="c-perfil" name="perfil"><option value="">Selecciona</option><option>Vivienda particular</option><option>Comunidad de vecinos</option><option>Nave industrial</option></select></div>
      {svc}
      <div class="field"><label for="c-msg">Describe lo que necesitas</label>
        <textarea id="c-msg" name="mensaje" rows="4" required minlength="10" placeholder="Ej.: qué ocurre, dónde, metros aproximados y si es urgente…"></textarea>
        <p class="hint">Cuanto más detalle, mejor podremos valorar el servicio y darte un presupuesto ajustado.</p>
      </div>
      <div class="hp" aria-hidden="true"><label>Web <input name="web" tabindex="-1" autocomplete="off"></label></div>
      <label class="check"><input type="checkbox" name="privacidad" required> <span>He leído y acepto la <a href="{root}ley-proteccion-datos/" target="_blank" rel="noopener">política de privacidad</a></span></label>
      <div class="send-row">
        <button type="submit" name="canal" value="email" class="btn btn-mail">{ic('mail',root)} Enviar por correo</button>
        <button type="submit" name="canal" value="whatsapp" class="btn btn-wa">{ic('chat',root)} Enviar por WhatsApp</button>
      </div>
      <p class="send-note">Si lo envías por WhatsApp, también recibimos una copia en nuestro correo.</p>
      {RGPD.replace('{root}',root)}
      <p class="form-msg" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>
'''

def footer(root):
    return f'''<footer class="site-foot">
  <div class="wrap foot-top">
    <div class="foot-brand">
      <img src="{root}assets/logo-blanco.png" alt="Grupo Urbanísima" width="260" height="51" loading="lazy">
      <p>Reparación de tejados, impermeabilización de terrazas y cubiertas, canalones y fachadas para particulares, comunidades de vecinos y empresas.</p>
      <div class="foot-cta">
        <a href="tel:{PHONE_TEL}" class="btn btn-sm">{ic('phone',root)} Llamar</a>
        <a href="https://wa.me/{WA}?text=Hola%2C%20quiero%20pedir%20presupuesto" class="btn btn-sm btn-wa" target="_blank" rel="noopener">{ic('chat',root)} WhatsApp</a>
      </div>
    </div>
    <nav class="foot-col" aria-label="Servicios">
      <h4>Servicios</h4>
      <a href="{root}servicios/">Todos los servicios</a>
      <a href="{root}servicios/{BY_KEY['goteras']['slug']}/">Reparación de goteras</a>
      <a href="{root}servicios/{BY_KEY['tejados']['slug']}/">Tejados</a>
      <a href="{root}servicios/{BY_KEY['impermeabilizacion']['slug']}/">Impermeabilización</a>
    </nav>
    <nav class="foot-col" aria-label="Más servicios">
      <h4>Más</h4>
      <a href="{root}servicios/{BY_KEY['fachadas']['slug']}/">Pintura de fachadas</a>
      <a href="{root}servicios/{BY_KEY['panel']['slug']}/">Panel sandwich</a>
      <a href="{root}servicios/{BY_KEY['chimeneas']['slug']}/">Chimeneas</a>
      <a href="{root}servicios/{BY_KEY['reforma']['slug']}/">Reforma integral</a>
    </nav>
    <div class="foot-col">
      <h4>Contacto</h4>
      <a href="tel:{PHONE_TEL}">{ic('phone',root)}{PHONE_TXT}</a>
      <a href="mailto:{MAIL}">{ic('mail',root)}{MAIL}</a>
      <span class="foot-note">{ic('check',root)}Servicio en toda la provincia de Valencia</span>
    </div>
  </div>
  <div class="wrap foot-legal">
    <div class="legal-left">
      <span>© <span id="year">2026</span> Grupo Urbanísima. Todos los derechos reservados.</span>
      <nav aria-label="Legal">
        <a href="{root}aviso-legal/">Aviso legal</a>
        <a href="{root}ley-proteccion-datos/">Privacidad</a>
        <a href="{root}aviso-ley-cookies/">Cookies</a>
        <a href="{root}condiciones/">Condiciones</a>
        <button type="button" class="link-btn" data-cookie-settings hidden>Configurar cookies</button>
      </nav>
    </div>
    <a class="sign" href="https://lestudio-crea.com" target="_blank" rel="noopener" aria-label="Desarrollado por Le Studio"><span>Desarrollado por</span><img src="{root}assets/lestudio-logo.png" alt="Le Studio" width="900" height="392" loading="lazy"></a>
  </div>
</footer>
<a class="fab" href="https://wa.me/{WA}?text=Hola%2C%20quiero%20pedir%20presupuesto" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp">{ic('chat',root)}<span>WhatsApp</span></a>
<div class="sticky-cta">
  <a href="tel:{PHONE_TEL}" class="btn btn-ghost-dark">{ic('phone',root)} Llamar</a>
  <a href="https://wa.me/{WA}?text=Hola%2C%20quiero%20pedir%20presupuesto" class="btn btn-wa" target="_blank" rel="noopener">{ic('chat',root)} WhatsApp</a>
</div>
</body>
</html>
'''

def jsonld(graph):
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>\n'

PROVIDER = {'@type': 'LocalBusiness', 'name': 'Grupo Urbanísima', 'telephone': PHONE_TEL, 'email': MAIL, 'url': SITE + '/',
            'address': {'@type': 'PostalAddress', 'streetAddress': 'Calle Jacinto Labaila 8b', 'addressLocality': 'Valencia', 'addressCountry': 'ES'}}

def service_page(s):
    root = '../../'
    url = f'{SITE}/servicios/{s["slug"]}/'
    title = f'{s["title"]} en Valencia | Grupo Urbanísima'
    h1 = f'{s["title"]} en Valencia'
    graph = [
      {'@type': 'Service', 'name': s['title'], 'serviceType': s['title'], 'description': s['intro'], 'url': url, 'provider': PROVIDER,
       'areaServed': {'@type': 'AdministrativeArea', 'name': 'Provincia de Valencia'}},
      {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Servicios', 'item': SITE + '/servicios/'},
        {'@type': 'ListItem', 'position': 3, 'name': s['title'], 'item': url}]},
      {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in s['faq']]},
    ]
    inc = ''.join(f'<li>{e(x)}</li>' for x in s['incluye'])
    sen = ''.join(f'<li>{e(x)}</li>' for x in s['senales'])
    faq = ''.join(f'<details{" open" if i == 0 else ""}><summary>{e(q)}{ic("chev",root)}</summary><p>{e(a)}</p></details>' for i, (q, a) in enumerate(s['faq']))
    rel = ''.join(f'<a class="rel-card" href="{root}servicios/{BY_KEY[k]["slug"]}/"><span class="ico">{ic(BY_KEY[k]["icon"],root)}</span><strong>{e(BY_KEY[k]["title"])}</strong><span class="rel-more">Ver servicio {ic("arrow",root)}</span></a>' for k in s['rel'])
    return (head(title, s['meta'], url, root, jsonld(graph)) + '<body class="sv-page" data-root="../../" data-servicio="' + e(s['title']) + '">\n' + header(root) + f'''
<main id="contenido">
<section class="sv-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Migas de pan"><a href="{root}">Inicio</a><span>›</span><a href="{root}servicios/">Servicios</a><span>›</span><span aria-current="page">{e(s["title"])}</span></nav>
    <div class="sv-hero-grid">
      <div>
        <h1>{e(h1)}</h1>
        <p class="lead">{e(s["intro"])}</p>
        <div class="cta-row">
          <a href="#contacto" class="btn btn-lg" data-cta="servicio">Solicitar presupuesto para {CTA[s["key"]]} {ic("arrow",root)}</a>
          <a href="tel:{PHONE_TEL}" class="btn btn-ghost btn-lg">{ic("phone",root)} 722 115 251</a>
        </div>
        <ul class="trust"><li>{ic("check",root)} Visita a domicilio sin coste</li><li>{ic("check",root)} Presupuesto sin compromiso</li><li>{ic("check",root)} Para viviendas, comunidades y naves industriales</li></ul>
      </div>
      <div class="sv-badge" aria-hidden="true">{ic(s["icon"],root)}</div>
    </div>
  </div>
</section>

<section class="section sv-body">
  <div class="wrap sv-grid">
    <div class="sv-main">
      <h2 id="que-hacemos">Qué hacemos</h2>
      <ul class="checklist">{inc}</ul>

      <h2>Cuándo necesitas este servicio</h2>
      <ul class="checklist soft">{sen}</ul>

      <h2 id="proceso">Cómo trabajamos</h2>
      <ol class="mini-steps">
        <li><b>1</b><strong>Visita sin coste</strong><span>Vamos a tu domicilio, local o edificio para ver el trabajo.</span></li>
        <li><b>2</b><strong>Presupuesto sin compromiso</strong><span>Te lo entregamos con el plan de trabajo y de seguridad.</span></li>
        <li><b>3</b><strong>Ejecución con garantía</strong><span>Trabajamos con las mejores marcas y gestionamos las licencias de obra si se necesitan.</span></li>
      </ol>

      <h2>Preguntas frecuentes</h2>
      <div class="faq">{faq}</div>
    </div>
    <aside class="sv-aside">
      <div class="aside-card">
        <h3>¿Hablamos?</h3>
        <p>Cuéntanos tu caso. Visita y presupuesto sin compromiso en toda la provincia de Valencia.</p>
        <a href="#contacto" class="btn btn-block" data-cta="servicio-lateral">Pedir presupuesto</a>
        <a href="tel:{PHONE_TEL}" class="btn btn-ghost-dark btn-block">{ic("phone",root)} {PHONE_TXT}</a>
        <a href="https://wa.me/{WA}?text=Hola%2C%20me%20interesa%3A%20{s["title"].replace(" ","%20")}" class="btn btn-wa btn-block" target="_blank" rel="noopener">{ic("chat",root)} WhatsApp</a>
        <small>Lunes a viernes, de 9:00 a 19:00</small>
      </div>
    </aside>
  </div>
</section>

<section class="section alt sv-rel">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Otros servicios</p><h2>También te puede interesar</h2></div>
    <div class="rel-grid">{rel}</div>
    <p class="more"><a class="link" href="{root}servicios/">Ver los 14 servicios {ic("arrow",root)}</a></p>
  </div>
</section>

''' + contact_section(root, f'Pide tu presupuesto de {s["title"].lower()}', s['title']) + '</main>\n\n' + footer(root))

def hub_page():
    root = '../'
    url = SITE + '/servicios/'
    title = 'Servicios de reparación y reformas en Valencia | Grupo Urbanísima'
    desc = 'Todos los servicios de Grupo Urbanísima en Valencia: tejados, impermeabilización, canalones, fachadas, panel sandwich, chimeneas, reformas y más. Presupuesto gratis.'
    graph = [
      {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Servicios', 'item': url}]},
      {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': s['title'], 'url': f'{SITE}/servicios/{s["slug"]}/'} for i, s in enumerate(SERVICES)]},
    ]
    cards = ''.join(f'''<a class="hub-card" data-slug="{s["key"]}" href="{s["slug"]}/" data-particulares="{s["rank"][0]}" data-comunidades="{s["rank"][1]}" data-empresas="{s["rank"][2]}">
      <span class="ico">{ic(s["icon"],root)}</span><h3>{e(s["title"])}</h3><p>{e(s["short"])}</p><ul class="bits">{"".join("<li>"+e(b)+"</li>" for b in s["bits"])}</ul><span class="rel-more">Ver servicio {ic("arrow",root)}</span></a>''' for s in SERVICES)
    return (head(title, desc, url, root, jsonld(graph)) + '<body class="sv-page" data-root="../">\n' + header(root) + f'''
<main id="contenido">
<section class="sv-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Migas de pan"><a href="{root}">Inicio</a><span>›</span><span aria-current="page">Servicios</span></nav>
    <h1>Servicios en Valencia para viviendas, comunidades y naves industriales</h1>
    <p class="lead">Tejados, terrazas y cubiertas, reparación de goteras, impermeabilización, reformas, chimeneas, canalones y pintura en toda la provincia de Valencia. Todos los servicios están disponibles para cualquier cliente: elige tu perfil y los ordenamos de más a menos solicitados.</p>
    <div class="cta-row"><a href="#contacto" class="btn btn-lg" data-cta="hub">Solicitar presupuesto gratuito {ic("arrow",root)}</a><a href="tel:{PHONE_TEL}" class="btn btn-ghost btn-lg">{ic("phone",root)} 722 115 251</a></div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="tabs" role="tablist" aria-label="Tipo de cliente">
      <button class="tab is-on" role="tab" aria-selected="true" data-filter="all">Todos</button>
      <button class="tab" role="tab" aria-selected="false" data-filter="particulares">{ic("home",root)}Viviendas particulares</button>
      <button class="tab" role="tab" aria-selected="false" data-filter="comunidades">{ic("building",root)}Comunidades</button>
      <button class="tab" role="tab" aria-selected="false" data-filter="empresas">{ic("factory",root)}Naves industriales</button>
    </div>
    <p class="svc-status" id="svc-status" aria-live="polite">Mostrando los 14 servicios</p>
    <div class="hub-grid" id="hub-grid">{cards}</div>
  </div>
</section>
''' + contact_section(root, 'Pide tu presupuesto gratis') + '</main>\n\n' + footer(root))

# ---------------------------------------------------------------- ESCRITURA
def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf8').write(content)

CTA = {  # texto del botón principal de cada página de servicio: "Solicitar presupuesto para ..."
 'tejados': 'reparar mi tejado', 'tejadosnuevos': 'un tejado nuevo', 'panel': 'mi cubierta o cerramiento', 'goteras': 'arreglar mis goteras',
 'terrazas': 'mi terraza', 'impermeabilizacion': 'impermeabilizar', 'reforma': 'mi reforma integral', 'pladur': 'trabajos de pladur',
 'banos': 'reformar mi baño', 'chimeneas': 'limpiar mi chimenea', 'desatasco': 'desatascar mi chimenea', 'canalones': 'limpiar mis canalones',
 'pinturainterior': 'pintar mi vivienda', 'fachadas': 'pintar mi fachada',
}

GROUPS = [  # clave, icono, título, descripción, servicios
 ('tejados', 'roof', 'Tejados y cubiertas', 'Rehabilitación, obra nueva y cerramientos para viviendas, edificios y naves.', ['tejados', 'tejadosnuevos', 'panel']),
 ('humedad', 'drop', 'Humedades e impermeabilización', 'Solución a goteras, filtraciones y terrazas con humedad.', ['goteras', 'impermeabilizacion', 'terrazas']),
 ('interior', 'home', 'Reformas interiores', 'Reformas integrales, baños, pladur y pintura para tu vivienda o local.', ['reforma', 'banos', 'pladur', 'pinturainterior']),
 ('fachadas', 'brush', 'Fachadas y mantenimiento', 'Pintura de fachadas, chimeneas y canalones, para mantener el edificio en buen estado.', ['fachadas', 'chimeneas', 'desatasco', 'canalones']),
]
assert sorted(k for g in GROUPS for k in g[4]) == sorted(x['key'] for x in SERVICES)

def options_html(indent='          '):
    out = ''
    for _, _, t, _, keys in GROUPS:
        out += f'\n{indent}<optgroup label="{e(t)}">' + ''.join(f'\n{indent}  <option>{e(BY_KEY[k]["title"])}</option>' for k in keys) + f'\n{indent}</optgroup>'
    return out + f'\n{indent}<option>Otro</option>\n'

def home_services():
    cols = ''
    for gk, icn, t, d, keys in GROUPS:
        items = ''.join(f'''
          <li data-slug="{k}" data-title="{e(BY_KEY[k]["title"])}"><a href="servicios/{BY_KEY[k]["slug"]}/"><span>{e(BY_KEY[k]["title"])}</span><svg class="i"><use href="#i-arrow"/></svg></a></li>''' for k in keys)
        cols += f'''
      <article class="grp grp-{gk}">
        <span class="ico"><svg class="i"><use href="#i-{icn}"/></svg></span>
        <h3>{e(t)}</h3>
        <p>{e(d)}</p>
        <ul class="grp-list">{items}
        </ul>
      </article>'''
    return f'''<!-- SERVICIOS-START -->
<section class="section" id="servicios">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">Nuestros servicios</p>
      <h2>Reformas y reparaciones, del tejado al interior</h2>
      <p class="sub">{len(SERVICES)} servicios para viviendas, comunidades de vecinos y naves industriales. Elige el que necesitas y pide presupuesto gratis.</p>
    </div>
    <div class="grp-grid">{cols}
    </div>
    <div class="car-more"><a href="servicios/" class="btn btn-lg">Ver todos los servicios <svg class="i"><use href="#i-arrow"/></svg></a>
      <a href="#hero-form" class="btn btn-ghost-dark btn-lg">Pedir presupuesto gratis</a></div>
  </div>
</section>
<!-- SERVICIOS-END -->
'''

def patch_home():
    path = os.path.join(ROOT, 'index.html')
    s = open(path, encoding='utf8').read()

    # 1) Sección de servicios (carrusel) y de problemas
    if '<!-- SERVICIOS-START -->' in s:
        i = s.index('<!-- SERVICIOS-START -->'); j = s.index('<!-- SERVICIOS-END -->') + len('<!-- SERVICIOS-END -->\n')
    else:
        i = s.index('<!-- SERVICIOS -->'); j = s.index('</section>', i) + len('</section>\n')
    s = s[:i] + home_services() + s[j:]
    # la sección "¿Qué necesitas resolver?" ya no existe (se unificó con los servicios)
    if '<!-- PROBLEMAS-START -->' in s:
        i = s.index('<!-- PROBLEMAS-START -->'); j = s.index('<!-- PROBLEMAS-END -->') + len('<!-- PROBLEMAS-END -->\n\n')
        s = s[:i] + s[j:]

    # 2) Desplegables de servicios (hero y contacto), agrupados
    for sid in ('servicio-select', 'hero-servicio'):
        s = re.sub(r'(<select id="%s" name="servicio">\s*<option value="">Selecciona un servicio</option>).*?(</select>)' % sid,
                   lambda m: m.group(1) + options_html() + '        ' + m.group(2), s, count=1, flags=re.S)

    # 3) Pie: enlaces por tipo de cliente y servicios principales
    def foot_links(*keys):
        return ''.join(f'\n      <a href="servicios/{BY_KEY[k]["slug"]}/">{e(lbl)}</a>' for k, lbl in keys)
    s = re.sub(r'<h4>Según quién seas</h4>.*?</nav>', '''<h4>Según quién seas</h4>
      <a href="servicios/?perfil=particulares">Viviendas particulares</a>
      <a href="servicios/?perfil=comunidades">Comunidades de vecinos</a>
      <a href="servicios/?perfil=empresas">Naves industriales</a>
      <a href="servicios/">Ver todos los servicios</a>
    </nav>''', s, count=1, flags=re.S)
    s = re.sub(r'<h4>Más solicitados</h4>.*?</nav>', '<h4>Más solicitados</h4>' + foot_links(
        ('goteras', 'Reparación de goteras'), ('tejados', 'Tejados'), ('impermeabilizacion', 'Impermeabilización'), ('fachadas', 'Pintura de fachadas'))
        + '\n      <a href="servicios/">Todos los servicios</a>\n    </nav>', s, count=1, flags=re.S)

    # 4) Título y texto del hero: reformas en general, del tejado al interior
    s = re.sub(r'<h1>.*?</h1>', '<h1>Reformas y reparaciones en Valencia, <em>del tejado al interior</em></h1>', s, count=1, flags=re.S)
    s = re.sub(r'<p class="lead">.*?</p>',
               '<p class="lead">Tejados, terrazas, goteras, reformas, baños, pintura y mantenimiento para viviendas, comunidades de vecinos y naves industriales. Vamos a tu domicilio, vemos el trabajo y te damos presupuesto <strong>gratis y sin compromiso</strong>.</p>', s, count=1, flags=re.S)
    title = 'Grupo Urbanísima | Reformas, tejados e impermeabilización en Valencia'
    desc = 'Tejados, terrazas y cubiertas, reparación de goteras, reformas, chimeneas, canalones y pintura en toda la provincia de Valencia. Presupuesto gratis y sin compromiso.'
    s = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), s, count=1)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + 'Reformas, tejados e impermeabilización en Valencia | Grupo Urbanísima' + m.group(2), s, count=1)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), s, count=1)
    open(path, 'w', encoding='utf8').write(s)

def build():
    base = os.path.join(ROOT, 'servicios')
    valid = {s['slug'] for s in SERVICES}
    if os.path.isdir(base):
        for d in os.listdir(base):
            if os.path.isdir(os.path.join(base, d)) and d not in valid: shutil.rmtree(os.path.join(base, d))
    patch_home()
    write('servicios/index.html', hub_page())
    for s in SERVICES:
        write(f'servicios/{s["slug"]}/index.html', service_page(s))

    # sitemap
    urls = [(SITE + '/', '1.0', 'monthly'), (SITE + '/servicios/', '0.9', 'monthly')]
    urls += [(f'{SITE}/servicios/{s["slug"]}/', '0.8', 'monthly') for s in SERVICES]
    urls += [(f'{SITE}/{p}/', '0.2', None) for p in ('aviso-legal', 'ley-proteccion-datos', 'aviso-ley-cookies', 'condiciones')]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u, pr, cf in urls:
        sm += f'  <url><loc>{u}</loc>' + (f'<changefreq>{cf}</changefreq>' if cf else '') + f'<priority>{pr}</priority></url>\n'
    write('sitemap.xml', sm + '</urlset>\n')

    # .htaccess: se conserva todo y se regeneran solo las redirecciones
    ht = open(os.path.join(ROOT, '.htaccess'), encoding='utf8').read()
    a = ht.index('# --- URLs antiguas'); b = ht.index('# --- Archivos antiguos')
    rules = ('# --- URLs antiguas -> web nueva (generado por scripts/build-services.py).\n'
             '#     QSA conserva los parámetros originales (gclid, utm_*): imprescindible para no perder la atribución de Google Ads.\n')
    allr = []
    for key, olds in OLD.items():
        for o in olds: allr.append((o, f'/servicios/{BY_KEY[key]["slug"]}/'))
    allr += list(OTHER_REDIRECTS.items()) + [(o, '/') for o in OLD_AC]
    for o, d in sorted(allr): rules += f'RewriteRule ^{o}/?$ {d} [R=301,L,QSA]\n'
    write('.htaccess', ht[:a] + rules + '\n' + ht[b:])
    return allr

if __name__ == '__main__':
    r = build()
    print(f'{len(SERVICES)} páginas de servicio + hub, sitemap y {len(r)} redirecciones generados.')
