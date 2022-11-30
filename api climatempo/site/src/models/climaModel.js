var database = require("../database/config");


function inserir(nomeLocal) {
    console.log("ACESSEI O AVISO MODEL \n \n\t\t >> Se aqui der erro de 'Error: connect ECONNREFUSED',\n \t\t >> verifique suas credenciais de acesso ao banco\n \t\t >> e se o servidor de seu BD está rodando corretamente. \n\n function pesquisarDescricao()");
    var inserir = `
    INSERT INTO lugar(nomeLocal) VALUES('${nomeLocal}')
    `;
    console.log("Executando a instrução SQL: \n" + inserir);
    return database.executar(inserir);
}

function tempLocal(fkLocal){
  instrucaoSql = ''


  if (process.env.AMBIENTE_PROCESSO == "producao") {
      instrucaoSql = 
      `select TOP 1 textoClima, temperatura, dataHora, (select nomeLocal from lugar where idLoc = ${fkLocal}) as nomeLocal from tempLocal where fkLocal = ${fkLocal} order by idCaptura desc`;
  } else if (process.env.AMBIENTE_PROCESSO == "desenvolvimento") {
          instrucaoSql = 
          `select textoClima, temperatura, dataHora, (select nomeLocal from lugar where idLoc = ${fkLocal}) as nomeLocal from tempLocal where fkLocal = ${fkLocal} order by idCaptura desc limit 1`
      } 
   else {
      console.log("\nO AMBIENTE (produção OU desenvolvimento) NÃO FOI DEFINIDO EM app.js\n");
      return
  }

  console.log("Executando a instrução SQL: \n" + instrucaoSql);
  return database.executar(instrucaoSql);
}

function tempSemana(fkLocal){
    instrucaoSql = ''


  if (process.env.AMBIENTE_PROCESSO == "producao") {
      instrucaoSql = 
      `select top 5 *, convert(varchar,diaMes,113) as datas from [dbo].[tempSemana] where fkLocal = ${fkLocal} order by diaMes asc;`;
  } else if (process.env.AMBIENTE_PROCESSO == "desenvolvimento") {
          instrucaoSql = 
          `select * from tempSemana order by fkLocal limit 4;`
      } 
   else {
      console.log("\nO AMBIENTE (produção OU desenvolvimento) NÃO FOI DEFINIDO EM app.js\n");
      return
  }

  console.log("Executando a instrução SQL: \n" + instrucaoSql);
  return database.executar(instrucaoSql);
}

//function publicar(titulo, descricao, idUsuario) {
 //   console.log("ACESSEI O AVISO MODEL \n \n\t\t >> Se aqui der erro de 'Error: connect ECONNREFUSED',\n \t\t >> verifique suas credenciais de acesso ao banco\n \t\t >> e se o servidor de seu BD está rodando corretamente. \n\n function publicar(): ", titulo, descricao, idUsuario);
 //   var instrucao = `
   //     INSERT INTO aviso (titulo, descricao, fk_usuario) VALUES ('${titulo}', '${descricao}', ${idUsuario});
  //  `;
   // console.log("Executando a instrução SQL: \n" + instrucao);
 //   return database.executar(instrucao);}



module.exports = {
    inserir,
    tempLocal,
    tempSemana
}
